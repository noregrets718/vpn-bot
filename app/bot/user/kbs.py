from urllib.parse import quote

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.config import settings
from app.utils.routing_profile import make_routing_deeplink

_APPSTORE_URL = "https://apps.apple.com/ru/app/happ-proxy-utility-plus/id6746188973?l=en-GB"
_GOOGLE_PLAY_URL = "https://play.google.com/store/apps/details?id=su.happ.mobile"


def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="Скачать клиент", callback_data="client_download"))
    kb.add(InlineKeyboardButton(text="Подключиться", callback_data="connect"))
    kb.add(InlineKeyboardButton(text="О проекте", callback_data="about_us"))

    if user_id in settings.ADMIN_IDS:
        kb.add(InlineKeyboardButton(text="🔐 Админ-панель", callback_data="admin_panel"))

    kb.adjust(1)
    return kb.as_markup()


def download_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="App Store (iOS)", url=_APPSTORE_URL))
    kb.add(InlineKeyboardButton(text="Google Play (Android)", url=_GOOGLE_PLAY_URL))
    kb.adjust(1)
    return kb.as_markup()


def connect_kb(happ_link: str) -> InlineKeyboardMarkup:
    sub_url = f"{settings.BASE_URL}/open-happ?link={quote(happ_link, safe='')}"
    routing_url = f"{settings.BASE_URL}/open-happ?link={quote(make_routing_deeplink(), safe='')}"
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Подключиться", url=sub_url))
    kb.add(InlineKeyboardButton(text="Настроить маршрутизацию", url=routing_url))
    kb.add(InlineKeyboardButton(text="Скопировать ссылку", callback_data="copy_sub_url"))
    kb.adjust(1)
    return kb.as_markup()