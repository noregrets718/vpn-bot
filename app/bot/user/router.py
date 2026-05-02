from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from loguru import logger

from app.bot.user.kbs import main_user_kb, download_kb, connect_kb
from app.bot.user.schemas import SUser, SUserFilter, SUserUpdateSubscription
from app.config import settings
from app.dao.dao import UserDAO
from app.services.remnawave import get_or_create_subscription, is_subscription_valid
from app.utils.happ import make_happ_link

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession, state: FSMContext):
    await state.clear()
    user_data = message.from_user
    user_id = user_data.id
    user_info = await UserDAO(session_with_commit).find_one_or_none_by_id(user_id)
    if user_info is None:
        user_schema = SUser(id=user_id, first_name=user_data.first_name,
                            last_name=user_data.last_name, username=user_data.username)
        await UserDAO(session_with_commit).add(user_schema)
    text = ("👋 Добро пожаловать в freedom VPN \n"
            "Используйте клавиатуру ниже, чтобы скачать клиент и подключиться")
    await message.answer(text, reply_markup=main_user_kb(user_id))


@router.callback_query(F.data == "client_download")
async def handle_client_download(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "Выберите платформу для скачивания Happ VPN:",
        reply_markup=download_kb(),
    )


@router.callback_query(F.data == "connect")
async def handle_connect(
    callback: CallbackQuery,
    session_with_commit: AsyncSession,
):
    await callback.answer()
    user = callback.from_user
    user_id = user.id
    dao = UserDAO(session_with_commit)

    user_record = await dao.find_one_or_none_by_id(user_id)
    subscription_url = user_record.subscription_url if user_record else None

    if subscription_url and not await is_subscription_valid(subscription_url):
        logger.warning(f"Stale subscription_url for user {user_id}, clearing cache")
        await dao.update(
            filters=SUserFilter(id=user_id),
            values=SUserUpdateSubscription(subscription_url=None),
        )
        subscription_url = None

    if not subscription_url:
        wait_msg = await callback.message.answer("Создаём ваш VPN-профиль, подождите...")
        try:
            subscription_url = await get_or_create_subscription(
                telegram_id=user_id,
                telegram_username=user.username,
            )
            await dao.update(
                filters=SUserFilter(id=user_id),
                values=SUserUpdateSubscription(subscription_url=subscription_url),
            )
        except Exception as e:
            logger.error(f"Remnawave error for user {user_id}: {e}")
            await wait_msg.delete()
            await callback.message.answer(
                "Не удалось создать VPN-профиль. Попробуйте позже или обратитесь к администратору."
            )
            return
        await wait_msg.delete()

    happ_link = await make_happ_link(subscription_url)

    if happ_link:
        await callback.message.answer(
            "Ваш VPN-профиль готов!\n\n"
            "Используйте кнопки ниже для подключения и настройки маршрутизации:",
            reply_markup=connect_kb(happ_link),
        )
    else:
        await callback.message.answer(
            "Ваш VPN-профиль готов!\n\n"
            f"Ссылка для подключения:\n<code>{subscription_url}</code>\n\n"
            "Скопируйте ссылку и добавьте её вручную в приложении Happ.",
        )


@router.callback_query(F.data == "copy_sub_url")
async def handle_copy_sub_url(callback: CallbackQuery, session_without_commit: AsyncSession):
    user_record = await UserDAO(session_without_commit).find_one_or_none_by_id(callback.from_user.id)
    if user_record and user_record.subscription_url:
        await callback.answer()
        await callback.message.answer(
            f"Ссылка для подключения:\n<code>{user_record.subscription_url}</code>"
        )
    else:
        await callback.answer("Подписка не найдена", show_alert=True)