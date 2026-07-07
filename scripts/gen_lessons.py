"""Deterministic V3 lesson generator.

Author lessons compactly (word list + grammar + dialogues); this expands
each spec into the full schema_version 2 lesson JSON (active_words, grammar,
dialogues, and 4 sections of interactive cards) matching the hand-written
Beginner lessons 1-6. English content only. No API calls.

Word tuple:  (en, ipa, pos, uz, ru, tj)
Grammar:     {"title": {uz,ru,tj}, "title_en": str, "rule": {uz,ru,tj}}
Dialogue:    {"scene": {uz,ru,tj}, "lines": [(speaker, en, ipa, uz, ru, tj), ...]}
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "static" / "course_v3_data"

UI = {
    "intro": {"uz": "Yangi so'zlar", "ru": "Новые слова", "tj": "Калимаҳои нав"},
    "grammar": {"uz": "Grammatika", "ru": "Грамматика", "tj": "Грамматика"},
    "practice": {"uz": "Mashq", "ru": "Практика", "tj": "Машқ"},
    "dialog": {"uz": "Dialog", "ru": "Диалог", "tj": "Муколама"},
    "meaning_q": {"uz": "Ma'nosi nima?", "ru": "Что означает?", "tj": "Маъно чист?"},
    "read_q": {"uz": "Qanday o'qiladi?", "ru": "Как читается?", "tj": "Чӣ хел хонда мешавад?"},
    "pick_word": {"uz": "So'zni tanlang", "ru": "Выберите слово", "tj": "Калимаро интихоб кунед"},
    "pick_right": {"uz": "To'g'ri javobni tanlang", "ru": "Выберите правильный ответ", "tj": "Ҷавоби дурустро интихоб кунед"},
    "heard": {"uz": "Eshitganingizni tanlang", "ru": "Выберите, что вы услышали", "tj": "Он чи шунидед, интихоб кунед"},
    "fill": {"uz": "Bo'sh joyga mos so'zni tanlang:", "ru": "Выберите подходящее слово:", "tj": "Калимаи мувофиқро интихоб кунед:"},
    "cloze": {"uz": "Dialogni to'ldiring", "ru": "Дополните диалог", "tj": "Муколамаро пурра кунед"},
}


def word_obj(no, w):
    en, ipa, pos, uz, ru, tj = w
    return {"no": no, "zh": en, "pinyin": ipa, "pos": pos, "meaning": {"uz": uz, "ru": ru, "tj": tj}}


def meaning(w):
    return {"uz": w[3], "ru": w[4], "tj": w[5]}


def others(words, keep, n=3):
    out = [x for x in words if x is not keep][:n]
    return out


def mg_prompt(word):
    return {"uz": f"«{word}» ma'nosini tanlang:", "ru": f"Выберите значение «{word}»:", "tj": f"Маънои «{word}»-ро интихоб кунед:"}


def build(spec):
    words = spec["words"]
    lvl, lid = spec["level"], spec["id"]

    active_words = [word_obj(i + 1, w) for i, w in enumerate(words)]

    grammar = []
    for i, g in enumerate(spec["grammar"], 1):
        grammar.append({"no": i, "title": g["title"], "title_en": g.get("title_en", ""), "rule": g["rule"]})

    dialogues = []
    for d in spec["dialogues"]:
        lines = [{"speaker": ln[0], "zh": ln[1], "pinyin": ln[2], "text": {"uz": ln[3], "ru": ln[4], "tj": ln[5]}} for ln in d["lines"]]
        dialogues.append({"scene": d["scene"], "dialogue": lines})

    # ---- Section 1: intro ----
    w = words
    s1 = []
    order = [0, 1, "mg", 2, 3, "hc", 4 if len(w) > 4 else 0, 5 if len(w) > 5 else 1, "pc", "mp"]
    used_active = set()
    for step in order:
        if step == "mg":
            tgt = w[0]
            opts = [meaning(tgt)] + [meaning(x) for x in others(w, tgt)]
            s1.append({"type": "meaning_guess", "prompt": mg_prompt(tgt[0]), "title": UI["meaning_q"], "options": opts, "correct_index": 0})
        elif step == "hc":
            tgt = w[min(4, len(w) - 1)]
            opts = [tgt[0]] + [x[0] for x in others(w, tgt)]
            s1.append({"type": "hanzi_choice", "prompt": {"uz": f"«{tgt[1]}» qaysi so'z?", "ru": f"Какое слово читается «{tgt[1]}»?", "tj": f"«{tgt[1]}» кадом калима аст?"}, "title": UI["pick_word"], "options": opts, "correct_index": 0})
        elif step == "pc":
            tgt = w[0]
            opts = [tgt[1]] + [x[1] for x in others(w, tgt)]
            s1.append({"type": "pinyin_choice", "prompt": {"uz": f"«{tgt[0]}» talaffuzini tanlang:", "ru": f"Выберите произношение «{tgt[0]}»:", "tj": f"Талаффузи «{tgt[0]}»-ро интихоб кунед:"}, "title": UI["read_q"], "options": opts, "correct_index": 0})
        elif step == "mp":
            pool = w[:4] if len(w) >= 4 else w
            s1.append({"type": "match_pairs", "pairs": [[x[0], meaning(x)] for x in pool]})
        else:
            idx = step
            if idx < len(w) and idx not in used_active:
                used_active.add(idx)
                s1.append({"type": "active_word", "word": word_obj(idx + 1, w[idx])})

    # ---- Section 2: grammar ----
    s2 = [{"type": "_grammar", "g": {"no": i + 1, "title": g["title"], "title_en": g.get("title_en", ""), "rule": g["rule"]}} for i, g in enumerate(spec["grammar"])]
    sb = spec.get("sentence_builder")
    if sb:
        s2.append({"type": "sentence_builder", "sentence": sb["sentence"], "tokens": sb["tokens"], "answer_tokens": sb["answer_tokens"], "explanation": sb["explanation"]})
    qq = spec.get("quiz_grammar")
    if qq:
        s2.append({"type": "quick_quiz", "prompt": qq["prompt"], "title": UI["pick_right"], "options": qq["options"], "correct_index": qq["correct_index"]})

    # ---- Section 3: practice ----
    s3 = []
    tgt = w[min(2, len(w) - 1)]
    s3.append({"type": "pinyin_choice", "prompt": {"uz": f"«{tgt[0]}» talaffuzini tanlang:", "ru": f"Выберите произношение «{tgt[0]}»:", "tj": f"Талаффузи «{tgt[0]}»-ро интихоб кунед:"}, "title": UI["read_q"], "options": [tgt[1]] + [x[1] for x in others(w, tgt)], "correct_index": 0})
    tgt2 = w[min(3, len(w) - 1)]
    s3.append({"type": "meaning_guess", "prompt": {"uz": f"«{tgt2[0]}» ma'nosini tanlang:", "ru": f"Выберите значение «{tgt2[0]}»:", "tj": f"Маънои «{tgt2[0]}»-ро интихоб кунед:"}, "title": UI["meaning_q"], "options": [meaning(tgt2)] + [meaning(x) for x in others(w, tgt2)], "correct_index": 0})
    lc = spec.get("listen_practice")
    if lc:
        s3.append({"type": "listening_choice", "title": UI["heard"], "audio_text": lc["audio_text"], "pinyin": lc["pinyin"], "options": lc["options"], "correct_index": lc["correct_index"], "explanation": lc["explanation"]})
    pool2 = w[-4:] if len(w) >= 4 else w
    s3.append({"type": "match_pairs", "pairs": [[x[0], meaning(x)] for x in pool2]})
    pr = spec.get("pronunciation")
    if pr:
        s3.append({"type": "pronunciation", "phrase": pr["phrase"], "pinyin": pr["pinyin"], "translation": pr["translation"]})

    # ---- Section 4: dialog ----
    s4 = []
    lc2 = spec.get("listen_dialog")
    if lc2:
        s4.append({"type": "listening_choice", "title": UI["heard"], "audio_text": lc2["audio_text"], "pinyin": lc2["pinyin"], "options": lc2["options"], "correct_index": lc2["correct_index"], "explanation": lc2["explanation"]})
    gf = spec.get("gap_fill")
    if gf:
        s4.append({"type": "gap_fill", "sentence": gf["sentence"], "prompt": UI["fill"], "options": gf["options"], "correct_index": gf["correct_index"], "explanation": gf["explanation"]})
    dc = spec.get("dialog_cloze")
    if dc:
        s4.append({"type": "dialog_cloze", "title": UI["cloze"], "lines": dc["lines"], "options": dc["options"], "correct_index": dc["correct_index"], "explanation": dc["explanation"]})
    qq2 = spec.get("quiz_dialog")
    if qq2:
        s4.append({"type": "quick_quiz", "prompt": qq2["prompt"], "title": UI["pick_right"], "options": qq2["options"], "correct_index": qq2["correct_index"]})

    lesson = {
        "schema_version": 2,
        "level": lvl,
        "lesson_id": lid,
        "title": spec["title"],
        "subtitle": spec["sub"],
        "intro_prebuilt": True,
        "grammar_prebuilt": True,
        "active_words": active_words,
        "grammar": grammar,
        "dialogues": dialogues,
        "sections": [
            {"section_no": 1, "section_title": UI["intro"], "section_purpose": "intro", "cards": s1},
            {"section_no": 2, "section_title": UI["grammar"], "section_purpose": "grammar", "cards": s2},
            {"section_no": 3, "section_title": UI["practice"], "section_purpose": "practice", "cards": s3},
            {"section_no": 4, "section_title": UI["dialog"], "section_purpose": "dialog", "cards": s4},
        ],
    }
    return lesson


def write_lesson(spec):
    lesson = build(spec)
    out = DATA / spec["level"] / f"lesson_{spec['id']:02d}.json"
    out.write_text(json.dumps(lesson, ensure_ascii=False, indent=2), encoding="utf-8")
    cjk = len([c for c in json.dumps(lesson, ensure_ascii=False) if "一" <= c <= "鿿"])
    return out, cjk


def update_manifest(level, lid, title_en, py, tr):
    for name in (DATA / f"{level}.json", ROOT / "app" / "static" / "course_data" / f"{level}.json"):
        if not name.exists():
            continue
        d = json.loads(name.read_text(encoding="utf-8"))
        for u in d.get("units", []):
            for les in u.get("lessons", []):
                if les.get("n") == lid:
                    les["zh"] = title_en
                    if "py" in les:
                        les["py"] = py
                    les["tr"] = tr
        name.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    import importlib.util
    spec_file = ROOT / "scripts" / "lesson_specs.py"
    s = importlib.util.spec_from_file_location("lesson_specs", spec_file)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    total = 0
    for spec in m.SPECS:
        out, cjk = write_lesson(spec)
        update_manifest(spec["level"], spec["id"], spec["manifest"]["title"], spec["manifest"]["py"], spec["manifest"]["tr"])
        flag = "" if cjk == 0 else f"  ⚠️ CJK={cjk}"
        print(f"  wrote {out.relative_to(ROOT)}  ({len(spec['words'])} words){flag}")
        total += 1
    print(f"Done. {total} lessons generated.")
