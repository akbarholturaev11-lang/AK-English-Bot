from datetime import datetime, timezone, timedelta

from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services.onboarding_service import OnboardingService
from app.bot.utils.i18n import t
from app.bot.keyboards.main_menu import main_menu_keyboard
from app.bot.keyboards.onboarding import language_keyboard, level_keyboard
from app.bot.fsm.onboarding import OnboardingStates


router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    session,
    command: CommandObject,
):
    service = OnboardingService(session)
    first_name = message.from_user.first_name if message.from_user and message.from_user.first_name else "Friend"

    referral_code = command.args if command and command.args else None

    user, created = await service.get_or_create_user(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name if message.from_user else None,
        username=message.from_user.username if message.from_user else None,
        referral_code=referral_code,
    )

    await state.clear()

    if not created and user.language and user.level:
        changed = False
        if user.learning_mode != "qa":
            user.learning_mode = "qa"
            changed = True
        if user.voice_mode != "none":
            user.voice_mode = "none"
            changed = True
        if changed:
            await session.commit()

        await message.answer(
            t("welcome_back", user.language, name=first_name),
            reply_markup=main_menu_keyboard(user.language),
        )
        return

    onboarding_msg = await message.answer(
        f"{t('welcome', user.language, name=first_name)}\n\n{t('choose_language', user.language)}",
        reply_markup=language_keyboard(),
    )

    await state.update_data(
        onboarding_message_id=onboarding_msg.message_id,
        first_name=first_name,
    )
    await state.set_state(OnboardingStates.choosing_language)


@router.callback_query(OnboardingStates.choosing_language)
async def process_language(callback: CallbackQuery, state: FSMContext, session):
    lang = callback.data.split(":")[1]

    service = OnboardingService(session)

    user, _ = await service.get_or_create_user(
        telegram_id=callback.from_user.id,
        full_name=callback.from_user.full_name if callback.from_user else None,
        username=callback.from_user.username if callback.from_user else None,
    )
    user.language = lang
    await session.commit()

    await callback.answer()

    data = await state.get_data()
    onboarding_message_id = data.get("onboarding_message_id")
    first_name = data.get("first_name", "Friend")

    try:
        if onboarding_message_id:
            await callback.bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=onboarding_message_id,
                text=f"{t('welcome', lang, name=first_name)}\n\n{t('choose_level', lang)}",
                reply_markup=level_keyboard(lang),
            )
    except Exception:
        pass

    await state.update_data(lang=lang)
    await state.set_state(OnboardingStates.choosing_level)


def _get_demo_lesson(level: str, lang: str) -> tuple:
    """Returns (display_text, ai_context) tuple."""

    challenges = {
        "beginner": {
            "tj": (
                "🎮 <b>Омода-ед? Бозӣ мекунем!</b>\n\n"
                "Ман ба шумо 3 калима медиҳам:\n\n"
                "✨ <b>Hello</b> · <b>Thank you</b> · <b>Goodbye</b>\n\n"
                "Аз ин калимаҳо як ҷумла созед — хато ҳам бошад, бот ислоҳ мекунад 😄",
                "The user just started learning English (beginner level). "
                "You gave them a challenge: make a sentence using Hello, Thank you, Goodbye. "
                "Their next message is their attempt. Encourage them, correct gently, explain the words."
            ),
            "uz": (
                "🎮 <b>Tayyor bo'ldingizmi? O'yin boshlanadi!</b>\n\n"
                "Sizga 3 ta so'z beraman:\n\n"
                "✨ <b>Hello</b> · <b>Thank you</b> · <b>Goodbye</b>\n\n"
                "Shu so'zlardan bitta gap tuzing — xato bo'lsa ham, bot tuzatadi 😄",
                "The user just started learning English (beginner level). "
                "You gave them a challenge: make a sentence using Hello, Thank you, Goodbye. "
                "Their next message is their attempt. Encourage them, correct gently, explain the words."
            ),
            "ru": (
                "🎮 <b>Готовы? Начинаем игру!</b>\n\n"
                "Даю вам 3 слова:\n\n"
                "✨ <b>Hello</b> · <b>Thank you</b> · <b>Goodbye</b>\n\n"
                "Составьте из них предложение — ошибки не страшны, бот поправит 😄",
                "The user just started learning English (beginner level). "
                "You gave them a challenge: make a sentence using Hello, Thank you, Goodbye. "
                "Their next message is their attempt. Encourage them, correct gently, explain the words."
            ),
        },
        "a1": {
            "tj": (
                "🎯 <b>A1 — Осон оғоз мекунем!</b>\n\n"
                "Ин 3 калимаро истифода баред:\n\n"
                "🔤 <b>I</b> · <b>am</b> · <b>student</b>\n\n"
                "Бо онҳо як ҷумлаи кӯтоҳи англисӣ созед.",
                "The user is English A1 level. You gave them a challenge: "
                "make a short sentence using I, am, student. Their next message is their attempt. Correct and encourage."
            ),
            "uz": (
                "🎯 <b>A1 — Osondan boshlaymiz!</b>\n\n"
                "Bu 3 so'zni ishlating:\n\n"
                "🔤 <b>I</b> · <b>am</b> · <b>student</b>\n\n"
                "Shular bilan bitta qisqa inglizcha gap tuzing.",
                "The user is English A1 level. You gave them a challenge: "
                "make a short sentence using I, am, student. Their next message is their attempt. Correct and encourage."
            ),
            "ru": (
                "🎯 <b>A1 — Начинаем просто!</b>\n\n"
                "Используйте эти 3 слова:\n\n"
                "🔤 <b>I</b> · <b>am</b> · <b>student</b>\n\n"
                "Составьте одно короткое английское предложение.",
                "The user is English A1 level. You gave them a challenge: "
                "make a short sentence using I, am, student. Their next message is their attempt. Correct and encourage."
            ),
        },
        "a2": {
            "tj": (
                "🕵️ <b>A2 — Ҷумларо табиӣ мекунем!</b>\n\n"
                "Ин калимаҳоро дар як ҷумла ҷамъ кунед:\n\n"
                "🇬🇧 <b>usually</b> · <b>study</b> · <b>evening</b>\n\n"
                "Як ҷумлаи оддӣ дар бораи рӯзи худ нависед.",
                "The user is English A2 level. You gave them a challenge: "
                "make a sentence about their day using usually, study, evening. "
                "Their next message is their attempt. Correct word order and grammar gently."
            ),
            "uz": (
                "🕵️ <b>A2 — Gapni tabiiy qilamiz!</b>\n\n"
                "Bu so'zlardan bitta gap tuzing:\n\n"
                "🇬🇧 <b>usually</b> · <b>study</b> · <b>evening</b>\n\n"
                "Kuningiz haqida oddiy inglizcha gap yozing.",
                "The user is English A2 level. You gave them a challenge: "
                "make a sentence about their day using usually, study, evening. "
                "Their next message is their attempt. Correct word order and grammar gently."
            ),
            "ru": (
                "🕵️ <b>A2 — Делаем фразу естественной!</b>\n\n"
                "Составьте одно предложение из этих слов:\n\n"
                "🇬🇧 <b>usually</b> · <b>study</b> · <b>evening</b>\n\n"
                "Напишите простое английское предложение о своём дне.",
                "The user is English A2 level. You gave them a challenge: "
                "make a sentence about their day using usually, study, evening. "
                "Their next message is their attempt. Correct word order and grammar gently."
            ),
        },
        "b1": {
            "tj": (
                "🔥 <b>B1 — Санҷиши зуд!</b>\n\n"
                "Ба ин савол бо англисӣ ҷавоб диҳед:\n\n"
                "🇬🇧 <b>What did you do yesterday?</b>\n\n"
                "2 ҷумла нависед.",
                "The user is English B1 level. You gave them a challenge: "
                "answer What did you do yesterday? in 2 English sentences. "
                "Their next message is their attempt. Evaluate grammar, correct errors, praise effort."
            ),
            "uz": (
                "🔥 <b>B1 — Tezkor sinov!</b>\n\n"
                "Bu savolga inglizcha javob bering:\n\n"
                "🇬🇧 <b>What did you do yesterday?</b>\n\n"
                "2 ta gap yozing.",
                "The user is English B1 level. You gave them a challenge: "
                "answer What did you do yesterday? in 2 English sentences. "
                "Their next message is their attempt. Evaluate grammar, correct errors, praise effort."
            ),
            "ru": (
                "🔥 <b>B1 — Быстрая проверка!</b>\n\n"
                "Ответьте по-английски на вопрос:\n\n"
                "🇬🇧 <b>What did you do yesterday?</b>\n\n"
                "Напишите 2 предложения.",
                "The user is English B1 level. You gave them a challenge: "
                "answer What did you do yesterday? in 2 English sentences. "
                "Their next message is their attempt. Evaluate grammar, correct errors, praise effort."
            ),
        },
        "b2": {
            "tj": (
                "⚡ <b>B2 — Услубро месанҷем!</b>\n\n"
                "Ин қолабро дар як ҷумла истифода баред:\n\n"
                "🇬🇧 <b>Although ..., ...</b>\n\n"
                "Аз зиндагии худатон мисол оред.",
                "The user is English B2 level. You gave them a challenge: "
                "use Although ..., ... in a sentence about their life. "
                "Their next message is their attempt. Analyze grammar, style, and suggest improvements."
            ),
            "uz": (
                "⚡ <b>B2 — Uslubni sinaymiz!</b>\n\n"
                "Bu grammatik patternni bitta gapda ishlating:\n\n"
                "🇬🇧 <b>Although ..., ...</b>\n\n"
                "O'z hayotingizdan misol keltiring.",
                "The user is English B2 level. You gave them a challenge: "
                "use Although ..., ... in a sentence about their life. "
                "Their next message is their attempt. Analyze grammar, style, and suggest improvements."
            ),
            "ru": (
                "⚡ <b>B2 — Проверим стиль!</b>\n\n"
                "Используйте эту конструкцию в одном предложении:\n\n"
                "🇬🇧 <b>Although ..., ...</b>\n\n"
                "Возьмите пример из своей жизни.",
                "The user is English B2 level. You gave them a challenge: "
                "use Although ..., ... in a sentence about their life. "
                "Their next message is their attempt. Analyze grammar, style, and suggest improvements."
            ),
        },
    }

    level_key = level.lower().replace(" ", "").replace("_", "")
    lang_key = lang if lang in ("tj", "uz", "ru") else "ru"

    level_map = {
        "beginner": "beginner", "az0": "beginner",
        "a1": "a1", "a2": "a2", "b1": "b1", "b2": "b2",
        "hsk1": "a1", "hsk2": "a2", "hsk3": "b1", "hsk4": "b2",
    }
    mapped = level_map.get(level_key, "beginner")
    result = challenges.get(mapped, {}).get(lang_key)
    if result:
        return result
    return ("", "")


@router.callback_query(OnboardingStates.choosing_level)
async def process_level(callback: CallbackQuery, state: FSMContext, session):
    level = callback.data.split(":")[1]

    service = OnboardingService(session)

    user, _ = await service.get_or_create_user(
        telegram_id=callback.from_user.id,
        full_name=callback.from_user.full_name if callback.from_user else None,
        username=callback.from_user.username if callback.from_user else None,
    )
    now = datetime.now(timezone.utc)
    user.level = level
    user.learning_mode = "qa"
    user.voice_mode = "none"
    user.status = "active"
    user.start_date = now
    user.end_date = now + timedelta(hours=24)
    user.expiry_reminder_sent_at = None
    await session.commit()

    await callback.answer()

    data = await state.get_data()
    onboarding_message_id = data.get("onboarding_message_id")

    user_num = str(user.id)

    try:
        if onboarding_message_id:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=onboarding_message_id,
            )
    except Exception:
        pass

    await callback.message.answer(
        t("onboarding_special_welcome", user.language, user_num=user_num),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(user.language),
    )

    display_text, ai_context = _get_demo_lesson(level, user.language)

    if display_text:
        await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=display_text,
            parse_mode="HTML",
        )

    if ai_context:
        from app.repositories.message_repo import MessageRepository
        msg_repo = MessageRepository(session)
        await msg_repo.create(
            user_id=user.id,
            role="system",
            content=ai_context,
            content_type="onboarding_challenge",
        )
        await session.commit()

    await state.clear()
