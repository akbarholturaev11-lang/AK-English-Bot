# -*- coding: utf-8 -*-
"""Replace IPA pronunciation with learner-friendly respellings in lesson JSONs.

- active_words / active_word cards / pronunciation single words -> respelling
- sentences (dialogue lines, listening audio, phrase sentences) -> "" (no IPA)
- hanzi_choice prompt (asks by pronunciation) -> rebuilt with respelling
- pinyin_choice options (IPA list) -> respellings
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from respell import RESPELL, respell  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def hanzi_prompt(re_word):
    return {"uz": f"«{re_word}» qaysi so'z?", "ru": f"Какое слово читается «{re_word}»?", "tj": f"«{re_word}» кадом калима аст?"}


def convert(path: Path) -> int:
    raw = path.read_text(encoding="utf-8")
    # Skip lessons that are still Chinese (contain CJK) — only de-IPA English ones.
    if any("一" <= ch <= "鿿" for ch in raw):
        return -1
    d = json.loads(raw)
    changed = 0

    # ipa -> respell (from this lesson's active words)
    ipa2re = {}
    for w in d.get("active_words", []):
        rs = respell(w.get("zh", ""))
        if w.get("pinyin"):
            ipa2re[w["pinyin"]] = rs
        w["pinyin"] = rs
        changed += 1

    for blk in d.get("dialogues", []):
        for ln in blk.get("dialogue", []):
            if ln.get("pinyin"):
                ln["pinyin"] = ""

    for sec in d.get("sections", []):
        for c in sec.get("cards", []):
            t = c.get("type")
            if t == "active_word":
                c["word"]["pinyin"] = respell(c["word"].get("zh", ""))
            elif t == "hanzi_choice":
                correct = c["options"][c["correct_index"]]
                c["prompt"] = hanzi_prompt(respell(correct))
            elif t == "pinyin_choice":
                c["options"] = [ipa2re.get(o, o if o in RESPELL.values() else "") for o in c["options"]]
            elif t == "listening_choice":
                if c.get("pinyin"):
                    c["pinyin"] = ""
            elif t == "pronunciation":
                c["pinyin"] = respell(c.get("phrase", ""))

    path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    # report leftover IPA-ish symbols
    txt = json.dumps(d, ensure_ascii=False)
    ipa_chars = sum(txt.count(ch) for ch in "ˈˌːɪæŋʊəɒɔːʃðθŋɡ")
    return ipa_chars


if __name__ == "__main__":
    files = sorted((ROOT / "app/static/course_v3_data").glob("*/lesson_*.json"))
    for f in files:
        left = convert(f)
        flag = "" if left == 0 else f"  ⚠️ IPA-ish left={left}"
        print(f"  {f.relative_to(ROOT)}{flag}")
    print(f"Done. {len(files)} lessons de-IPA'd.")
