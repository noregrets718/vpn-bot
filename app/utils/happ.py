import httpx
from loguru import logger

_CRYPTO_API_URL = "https://crypto.happ.su/api-v2.php"


async def  make_happ_link(subscription_url: str) -> str | None:
    """
    Шифрует subscription URL через Happ Crypto API.
    Возвращает happ://crypt5/... ссылку или None при ошибке.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                _CRYPTO_API_URL,
                json={"url": subscription_url},
            )
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "json" in content_type:
                data = response.json()
                if isinstance(data, str):
                    return data
                return (
                    data.get("encrypted_link")
                    or data.get("link")
                    or data.get("url")
                    or data.get("result")
                )
            else:
                text = response.text.strip()
                return text if text.startswith("happ://") else None

    except Exception as e:
        logger.warning(f"Happ Crypto API error: {e}")
        return None