"""Seed course_lessons from the authored English course JSON.

The Chinese course seeded this table from ~75 hand-written scripts under
scripts/. Those are gone: the English course lives in
app/static/course_v3_data/<level>/lesson_NN.json, and that is now the single
source of truth for both the Mini App and the DB-backed features
(practice questions, AI Voice review, the bot's course mode).

The JSON keeps translations as {"uz": ..., "ru": ..., "tj": ...} dicts, while
the DB readers expect flat per-language keys next to the term, so the mapping
below flattens them.
"""

import json
from pathlib import Path

from sqlalchemy import func, select

from app.db.models.course_lessons import CourseLesson

COURSE_V3_DIR = Path(__file__).resolve().parents[1] / "static" / "course_v3_data"
LEVELS = ("hsk1", "hsk2", "hsk3", "hsk4")
LANGS = ("uz", "ru", "tj")


def _localized(value, lang: str) -> str:
    """{"uz": ...} -> the one string; plain strings pass through."""
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("uz") or value.get("ru") or value.get("tj") or "")
    return str(value or "")


def _spread(target: dict, value, prefix: str = "") -> None:
    """Write uz/ru/tj keys onto `target` (optionally as `<prefix>_<lang>`)."""
    for lang in LANGS:
        target[f"{prefix}_{lang}" if prefix else lang] = _localized(value, lang)


def _vocabulary(words: list) -> list[dict]:
    items = []
    for index, word in enumerate(words or [], 1):
        if not isinstance(word, dict):
            continue
        item = {
            "no": int(word.get("no") or index),
            "zh": word.get("zh") or "",
            "pinyin": word.get("pinyin") or "",
            "pos": word.get("pos") or "",
        }
        _spread(item, word.get("meaning"))
        items.append(item)
    return items


def _grammar(entries: list) -> list[dict]:
    items = []
    for index, entry in enumerate(entries or [], 1):
        if not isinstance(entry, dict):
            continue
        item = {"no": int(entry.get("no") or index), "title_zh": entry.get("title_zh") or ""}
        _spread(item, entry.get("title"), "title")
        _spread(item, entry.get("rule"), "rule")
        examples = []
        for example in entry.get("examples") or []:
            if not isinstance(example, dict):
                continue
            built = {"zh": example.get("zh") or "", "pinyin": example.get("pinyin") or ""}
            _spread(built, example.get("text") or example.get("translation"))
            examples.append(built)
        item["examples"] = examples
        items.append(item)
    return items


def _dialogue_blocks(dialogues: list, word_count: int, grammar_count: int) -> list[dict]:
    """One block per scene. The bot's course formatter keys off block_no, and
    word_nos/grammar_nos decide which vocabulary and grammar a block shows —
    the JSON has no such split, so every block carries the whole lesson."""
    word_nos = list(range(1, word_count + 1))
    grammar_nos = list(range(1, grammar_count + 1))
    blocks = []
    for index, scene in enumerate(dialogues or [], 1):
        if not isinstance(scene, dict):
            continue
        lines = []
        for line in scene.get("dialogue") or []:
            if not isinstance(line, dict):
                continue
            built = {
                "speaker": line.get("speaker") or "",
                "zh": line.get("zh") or "",
                "pinyin": line.get("pinyin") or "",
            }
            _spread(built, line.get("text"))
            lines.append(built)
        block = {
            "block_no": index,
            "dialogue": lines,
            "word_nos": word_nos,
            "grammar_nos": grammar_nos,
        }
        _spread(block, scene.get("scene"), "scene")
        blocks.append(block)
    return blocks


def lesson_row(payload: dict) -> dict | None:
    """One authored lesson JSON -> CourseLesson column values."""
    level = str(payload.get("level") or "").strip().lower()
    order = int(payload.get("lesson_id") or 0)
    if level not in LEVELS or order <= 0:
        return None
    words = payload.get("active_words") or []
    grammar = payload.get("grammar") or []
    return {
        "level": level,
        "lesson_order": order,
        "lesson_code": f"{level.upper()}-L{order:02d}",
        "title": str(payload.get("title") or ""),
        "goal": _localized(payload.get("subtitle"), "uz"),
        "intro_text": "",
        "vocabulary_json": json.dumps(_vocabulary(words), ensure_ascii=False),
        "dialogue_json": json.dumps(
            _dialogue_blocks(payload.get("dialogues"), len(words), len(grammar)),
            ensure_ascii=False,
        ),
        "grammar_json": json.dumps(_grammar(grammar), ensure_ascii=False),
        "exercise_json": "[]",
        "answers_json": "[]",
        "homework_json": "[]",
        "review_json": "[]",
        "is_active": True,
    }


class CourseSeedService:
    def __init__(self, session):
        self.session = session

    async def count_lessons(self) -> int:
        count = await self.session.scalar(select(func.count()).select_from(CourseLesson))
        return int(count or 0)

    async def sync_all_lessons(self) -> int:
        for path in self._iter_lesson_paths():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            row = lesson_row(payload)
            if row:
                await self._upsert(row)
        await self.session.commit()
        return await self.count_lessons()

    def _iter_lesson_paths(self) -> list[Path]:
        paths: list[Path] = []
        for level in LEVELS:
            paths.extend(sorted((COURSE_V3_DIR / level).glob("lesson_*.json")))
        return paths

    async def _upsert(self, row: dict) -> None:
        existing = await self.session.scalar(
            select(CourseLesson).where(CourseLesson.lesson_code == row["lesson_code"])
        )
        if existing is None:
            self.session.add(CourseLesson(**row))
            return
        for key, value in row.items():
            setattr(existing, key, value)
