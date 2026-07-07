import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


# English course — Beginner, Lesson 1.
# Data contract (kept from the original design, repurposed for English):
#   zh     -> the English word / phrase (shown large in the mini app)
#   pinyin -> pronunciation (shown small under the word)
#   uz/ru/tj -> meaning in the learner's own language
LESSON = {
    "level": "hsk1",
    "lesson_order": 1,
    "lesson_code": "HSK1-L01",
    "title": json.dumps({
        "en": "Greetings & Politeness",
        "uz": "Salomlashish va xushmuomalalik",
        "ru": "Приветствия и вежливость",
        "tj": "Салом ва хушмуомилагӣ",
    }, ensure_ascii=False),
    "goal": json.dumps({
        "uz": "Ingliz tilida salomlashish, xayrlashish va xushmuomala so'zlarni o'rganing",
        "ru": "Научитесь здороваться, прощаться и быть вежливым на английском",
        "tj": "Ба забони англисӣ салом гуфтан, хайрухуш ва хушмуомилагиро омӯзед",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "Birinchi darsda siz ingliz tilida salomlashishni o'rganasiz. Bu dars 8 ta yangi so'z, 3 ta dialog va asosiy talaffuz qoidalarini o'z ichiga oladi.",
        "ru": "На первом уроке вы научитесь английским приветствиям. Урок включает 8 новых слов, 3 диалога и основные правила произношения.",
        "tj": "Дар дарси аввал шумо салом гуфтан ба забони англисиро меомӯзед. Ин дарс 8 калимаи нав, 3 муколама ва қоидаҳои асосии талаффузро дар бар мегирад.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "Hello", "pinyin": "/həˈloʊ/", "pos": "interj.",
         "uz": "salom (umumiy)",
         "ru": "привет / здравствуйте",
         "tj": "салом (умумӣ)"},
        {"no": 2, "zh": "Hi", "pinyin": "/haɪ/", "pos": "interj.",
         "uz": "salom (norasmiy)",
         "ru": "привет (неформально)",
         "tj": "салом (ғайрирасмӣ)"},
        {"no": 3, "zh": "Good morning", "pinyin": "/ɡʊd ˈmɔːrnɪŋ/", "pos": "expr.",
         "uz": "xayrli tong",
         "ru": "доброе утро",
         "tj": "субҳ ба хайр"},
        {"no": 4, "zh": "Goodbye", "pinyin": "/ɡʊdˈbaɪ/", "pos": "interj.",
         "uz": "xayr",
         "ru": "до свидания",
         "tj": "хайр"},
        {"no": 5, "zh": "Please", "pinyin": "/pliːz/", "pos": "adv.",
         "uz": "iltimos",
         "ru": "пожалуйста (просьба)",
         "tj": "лутфан"},
        {"no": 6, "zh": "Thank you", "pinyin": "/ˈθæŋk juː/", "pos": "expr.",
         "uz": "rahmat",
         "ru": "спасибо",
         "tj": "ташаккур"},
        {"no": 7, "zh": "Sorry", "pinyin": "/ˈsɒri/", "pos": "interj.",
         "uz": "kechirasiz, uzr",
         "ru": "извините, простите",
         "tj": "бубахшед"},
        {"no": 8, "zh": "You're welcome", "pinyin": "/jʊr ˈwelkəm/", "pos": "expr.",
         "uz": "arzimaydi (rahmatga javob)",
         "ru": "пожалуйста (в ответ на спасибо)",
         "tj": "хоҳиш мекунам"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "Dialogue 1",
            "scene_uz": "Ikki do'st uchrashadi",
            "scene_ru": "Встречаются два друга",
            "scene_tj": "Ду дӯст вомехӯранд",
            "dialogue": [
                {"speaker": "A", "zh": "Hello!", "pinyin": "/həˈloʊ/",
                 "uz": "Salom!", "ru": "Привет!", "tj": "Салом!"},
                {"speaker": "B", "zh": "Hi! Good morning!", "pinyin": "/haɪ ɡʊd ˈmɔːrnɪŋ/",
                 "uz": "Salom! Xayrli tong!", "ru": "Привет! Доброе утро!", "tj": "Салом! Субҳ ба хайр!"},
            ]
        },
        {
            "block_no": 2,
            "section_label": "Dialogue 2",
            "scene_uz": "Xushmuomala javob",
            "scene_ru": "Вежливый ответ",
            "scene_tj": "Ҷавоби хушмуомила",
            "dialogue": [
                {"speaker": "A", "zh": "Thank you!", "pinyin": "/ˈθæŋk juː/",
                 "uz": "Rahmat!", "ru": "Спасибо!", "tj": "Ташаккур!"},
                {"speaker": "B", "zh": "You're welcome!", "pinyin": "/jʊr ˈwelkəm/",
                 "uz": "Arzimaydi!", "ru": "Пожалуйста!", "tj": "Хоҳиш мекунам!"},
            ]
        },
        {
            "block_no": 3,
            "section_label": "Dialogue 3",
            "scene_uz": "Kechirim so'rash",
            "scene_ru": "Извинение",
            "scene_tj": "Узрпурсӣ",
            "dialogue": [
                {"speaker": "A", "zh": "Sorry!", "pinyin": "/ˈsɒri/",
                 "uz": "Kechirasiz!", "ru": "Извините!", "tj": "Бубахшед!"},
                {"speaker": "B", "zh": "No problem!", "pinyin": "/noʊ ˈprɒbləm/",
                 "uz": "Muammo yo'q!", "ru": "Ничего страшного!", "tj": "Мушкиле нест!"},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_en": "Formal vs informal greetings",
            "title_uz": "Rasmiy va norasmiy salomlashish",
            "title_ru": "Формальные и неформальные приветствия",
            "title_tj": "Салому алейки расмӣ ва ғайрирасмӣ",
            "rule_uz": (
                "Ingliz tilida salomlashish vaziyatga qarab tanlanadi:\n"
                "• Norasmiy: Hi / Hey — do'stlar bilan\n"
                "• Umumiy: Hello — deyarli har doim mos\n"
                "• Rasmiy: Good morning / Good afternoon / Good evening\n\n"
                "Rasmiy vaziyatda 'Hi' emas, 'Hello' yoki 'Good morning' ishlatiladi."
            ),
            "rule_ru": (
                "В английском приветствие выбирается по ситуации:\n"
                "• Неформально: Hi / Hey — с друзьями\n"
                "• Нейтрально: Hello — подходит почти всегда\n"
                "• Формально: Good morning / Good afternoon / Good evening\n\n"
                "В формальной ситуации используйте 'Hello' или 'Good morning', а не 'Hi'."
            ),
            "rule_tj": (
                "Дар забони англисӣ салом аз рӯи вазъият интихоб мешавад:\n"
                "• Ғайрирасмӣ: Hi / Hey — бо дӯстон\n"
                "• Умумӣ: Hello — қариб ҳамеша мувофиқ\n"
                "• Расмӣ: Good morning / Good afternoon / Good evening\n\n"
                "Дар вазъияти расмӣ 'Hello' ё 'Good morning' гӯед, на 'Hi'."
            ),
            "examples": [
                {"zh": "Hi, Tom!", "pinyin": "/haɪ tɒm/",
                 "uz": "Salom, Tom! (norasmiy)", "ru": "Привет, Том! (неформ.)", "tj": "Салом, Том! (ғайрирасмӣ)"},
                {"zh": "Good morning, Mr. Lee.", "pinyin": "/ɡʊd ˈmɔːrnɪŋ ˈmɪstər liː/",
                 "uz": "Xayrli tong, janob Li. (rasmiy)", "ru": "Доброе утро, мистер Ли. (формально)", "tj": "Субҳ ба хайр, ҷаноби Ли. (расмӣ)"},
            ]
        },
        {
            "no": 2,
            "title_en": "Responding to 'Thank you'",
            "title_uz": "'Thank you' ga javob berish",
            "title_ru": "Ответ на 'Thank you'",
            "title_tj": "Ҷавоб ба 'Thank you'",
            "rule_uz": (
                "Kimdir 'Thank you' desa, quyidagicha javob beriladi:\n"
                "• You're welcome — eng keng tarqalgan, xushmuomala\n"
                "• No problem — norasmiy, do'stona\n\n"
                "'Sorry' ga esa 'No problem' yoki 'It's okay' deb javob beriladi."
            ),
            "rule_ru": (
                "Когда кто-то говорит 'Thank you', отвечают так:\n"
                "• You're welcome — самое распространённое, вежливое\n"
                "• No problem — неформально, по-дружески\n\n"
                "На 'Sorry' отвечают 'No problem' или 'It's okay'."
            ),
            "rule_tj": (
                "Вақте касе 'Thank you' мегӯяд, чунин ҷавоб медиҳанд:\n"
                "• You're welcome — маъмултарин, хушмуомила\n"
                "• No problem — ғайрирасмӣ, дӯстона\n\n"
                "Ба 'Sorry' бошад 'No problem' ё 'It's okay' ҷавоб медиҳанд."
            ),
            "examples": [
                {"zh": "A: Thank you! B: You're welcome!", "pinyin": "/ˈθæŋk juː — jʊr ˈwelkəm/",
                 "uz": "A: Rahmat! B: Arzimaydi!", "ru": "A: Спасибо! B: Пожалуйста!", "tj": "A: Ташаккур! B: Хоҳиш мекунам!"},
                {"zh": "A: Sorry! B: No problem!", "pinyin": "/ˈsɒri — noʊ ˈprɒbləm/",
                 "uz": "A: Kechirasiz! B: Muammo yo'q!", "ru": "A: Извините! B: Ничего страшного!", "tj": "A: Бубахшед! B: Мушкиле нест!"},
            ]
        },
    ], ensure_ascii=False),

    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_english",
            "instruction_uz": "Quyidagilarni ingliz tilida yozing:",
            "instruction_ru": "Напишите по-английски:",
            "instruction_tj": "Ба забони англисӣ нависед:",
            "items": [
                {"prompt_uz": "salom (umumiy)", "prompt_ru": "привет (нейтрально)", "prompt_tj": "салом (умумӣ)", "answer": "Hello", "pinyin": "/həˈloʊ/"},
                {"prompt_uz": "xayrli tong", "prompt_ru": "доброе утро", "prompt_tj": "субҳ ба хайр", "answer": "Good morning", "pinyin": "/ɡʊd ˈmɔːrnɪŋ/"},
                {"prompt_uz": "rahmat", "prompt_ru": "спасибо", "prompt_tj": "ташаккур", "answer": "Thank you", "pinyin": "/ˈθæŋk juː/"},
                {"prompt_uz": "kechirasiz", "prompt_ru": "извините", "prompt_tj": "бубахшед", "answer": "Sorry", "pinyin": "/ˈsɒri/"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холиро пур кунед:",
            "items": [
                {"prompt_uz": "A: Thank you!  B: You're ___!", "prompt_ru": "A: Thank you!  B: You're ___!", "prompt_tj": "A: Thank you!  B: You're ___!", "answer": "welcome", "pinyin": "/ˈwelkəm/"},
                {"prompt_uz": "A: ___!  B: Hi!", "prompt_ru": "A: ___!  B: Hi!", "prompt_tj": "A: ___!  B: Hi!", "answer": "Hello", "pinyin": "/həˈloʊ/"},
                {"prompt_uz": "A: Sorry!  B: No ___!", "prompt_ru": "A: Sorry!  B: No ___!", "prompt_tj": "A: Sorry!  B: No ___!", "answer": "problem", "pinyin": "/ˈprɒbləm/"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["Hello", "Good morning", "Thank you", "Sorry"]},
        {"no": 2, "answers": ["welcome", "Hello", "problem"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Quyidagi so'zlardan foydalanib 2 ta qisqa dialog yozing:",
            "instruction_ru": "Напишите 2 коротких диалога, используя следующие слова:",
            "instruction_tj": "Бо истифодаи калимаҳои зерин 2 муколамаи кӯтоҳ нависед:",
            "words": ["Hello", "Good morning", "Thank you", "You're welcome", "Sorry"],
            "example": "A: Sorry! B: No problem!",
        },
        {
            "no": 2,
            "instruction_uz": "So'zlarni baland ovozda talaffuz qiling va yozib mashq qiling:",
            "instruction_ru": "Произнесите слова вслух и отработайте их письменно:",
            "instruction_tj": "Калимаҳоро баланд талаффуз кунед ва навишта машқ кунед:",
            "words": [
                {"zh": "Hello", "pinyin": "/həˈloʊ/", "uz": "salom", "ru": "привет", "tj": "салом"},
                {"zh": "Thank you", "pinyin": "/ˈθæŋk juː/", "uz": "rahmat", "ru": "спасибо", "tj": "ташаккур"},
                {"zh": "Goodbye", "pinyin": "/ɡʊdˈbaɪ/", "uz": "xayr", "ru": "до свидания", "tj": "хайр"},
            ]
        }
    ], ensure_ascii=False),

    "is_active": True,
}


async def seed():
    async with SessionLocal() as session:
        result = await session.execute(
            select(CourseLesson).where(CourseLesson.lesson_code == LESSON["lesson_code"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in LESSON.items():
                setattr(existing, key, value)
            await session.commit()
            print(f"✅ Lesson {LESSON['lesson_code']} updated (English).")
        else:
            lesson = CourseLesson(**LESSON)
            session.add(lesson)
            await session.commit()
            print(f"✅ Lesson {LESSON['lesson_code']} created (English).")


if __name__ == "__main__":
    asyncio.run(seed())
