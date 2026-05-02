import re
from datetime import datetime, timedelta, timezone

import httpx
from loguru import logger

from app.config import settings

# Remnawave username: ^[a-zA-Z0-9_-]+$, длина 3-36 символов
_USERNAME_RE = re.compile(r'^[a-zA-Z0-9_-]{3,36}$')


def _build_username(telegram_id: int, telegram_username: str | None) -> str:
    """Использует Telegram username если подходит, иначе tg{id}."""
    if telegram_username and _USERNAME_RE.match(telegram_username):
        return telegram_username
    return f"tg{telegram_id}"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.REMNAWAVE_API_TOKEN}"}


async def is_subscription_valid(subscription_url: str) -> bool:
    """Проверяет, возвращает ли subscription URL корректный ответ (не 404)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.head(subscription_url)
            return resp.status_code not in (404, 400)
    except Exception as e:
        logger.warning(f"Subscription URL validation failed: {e}")
        return False


async def get_or_create_subscription(
    telegram_id: int,
    telegram_username: str | None = None,
) -> str:
    """
    Возвращает subscription_url пользователя.
    Сначала ищет по telegramId, при отсутствии — создаёт нового.
    """
    base = settings.REMNAWAVE_URL.rstrip("/")

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Поиск существующего пользователя по Telegram ID
        resp = await client.get(
            f"{base}/api/users/by-telegram-id/{telegram_id}",
            headers=_headers(),
        )

        if resp.status_code == 200:
            data = resp.json()
            users = data.get("response", [])
            if users:
                sub_url = users[0].get("subscriptionUrl")
                if sub_url:
                    logger.info(f"Remnawave: found user by telegramId={telegram_id}")
                    return sub_url

        # Создаём нового пользователя
        username = _build_username(telegram_id, telegram_username)
        expire_at = datetime.now(timezone.utc) + timedelta(days=settings.REMNAWAVE_EXPIRE_DAYS)

        create_resp = await client.post(
            f"{base}/api/users",
            headers=_headers(),
            json={
                "username": username,
                "expireAt": expire_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "telegramId": telegram_id,
                "activeInternalSquads": settings.squad_ids,
            },
        )
        create_resp.raise_for_status()

        data = create_resp.json()
        user = data.get("response", data)
        sub_url = user.get("subscriptionUrl")

        if not sub_url:
            raise ValueError(
                f"Remnawave did not return subscriptionUrl for {username}. Response: {data}"
            )

        logger.info(f"Remnawave: created user '{username}' (telegramId={telegram_id})")
        return sub_url