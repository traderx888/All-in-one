"""Send posts to a Telegram channel or group via Bot API."""

from __future__ import annotations
import requests
from workflow import config

_BASE = "https://api.telegram.org/bot{token}"


def send_post(text: str, parse_mode: str = "Markdown") -> dict:
    """Send *text* to the configured Telegram chat. Returns API response."""
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env"
        )

    url = f"{_BASE.format(token=config.TELEGRAM_BOT_TOKEN)}/sendMessage"

    # Telegram has a 4096-char limit per message; split if needed.
    chunks = _split_message(text, limit=4096)
    result = {}
    for chunk in chunks:
        resp = requests.post(
            url,
            json={
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": chunk,
                "parse_mode": parse_mode,
                "disable_web_page_preview": False,
            },
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()

    return result


def _split_message(text: str, limit: int = 4096) -> list[str]:
    """Split text into chunks that fit within *limit* characters."""
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        # Try to split at a newline near the limit
        split_at = text.rfind("\n", 0, limit)
        if split_at < limit // 2:
            split_at = limit  # no good newline found, hard split
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks
