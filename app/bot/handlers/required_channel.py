from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.bot.utils.i18n import t
from app.repositories.user_repo import UserRepository
from app.services.required_channel_service import RequiredChannelService


router = Router()


@router.callback_query(F.data == "force_sub:check")
async def force_sub_check(callback: CallbackQuery, session):
    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    lang = user.language if user and user.language else "ru"
    service = RequiredChannelService(session)
    missing = await service.missing_channels(callback.bot, callback.from_user.id)
    if missing:
        await callback.answer(t("force_sub_still_missing", lang), show_alert=True)
        if callback.message:
            await callback.message.edit_text(
                service.build_required_text(missing, lang),
                reply_markup=service.build_required_keyboard(missing, lang),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        return

    await callback.answer(t("force_sub_unlocked_alert", lang), show_alert=True)
    if callback.message:
        try:
            await callback.message.delete()
        except Exception:
            await callback.message.edit_text(t("force_sub_unlocked_text", lang), parse_mode="HTML")
