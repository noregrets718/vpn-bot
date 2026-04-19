from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.config import settings


def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="Скачать клиент", callback_data="client_download"))
    kb.add(InlineKeyboardButton(text="Подключиться", callback_data="connect"))
    kb.add(InlineKeyboardButton(text="О проекте", callback_data="about_us"))

    if user_id in settings.ADMIN_IDS:
        kb.add(InlineKeyboardButton(text="🔐 Админ-панель", callback_data="admin_panel"))

    kb.adjust(1)
    return kb.as_markup()