"""Centralised configuration loaded from .env"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _get(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


# Notion
NOTION_API_KEY = _get("NOTION_API_KEY")
NOTION_DATABASE_ID = _get("NOTION_DATABASE_ID")
NOTION_STYLE_PAGE_IDS = [
    pid.strip()
    for pid in _get("NOTION_STYLE_PAGE_IDS").split(",")
    if pid.strip()
]

# Telegram
TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _get("TELEGRAM_CHAT_ID")

# Patreon
PATREON_ACCESS_TOKEN = _get("PATREON_ACCESS_TOKEN")
PATREON_CAMPAIGN_ID = _get("PATREON_CAMPAIGN_ID")

# YouTube
YOUTUBE_CLIENT_SECRETS_FILE = _get("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
YOUTUBE_CHANNEL_ID = _get("YOUTUBE_CHANNEL_ID")

# OpenAI-compatible LLM
OPENAI_API_KEY = _get("OPENAI_API_KEY")
OPENAI_BASE_URL = _get("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = _get("OPENAI_MODEL", "gpt-4o")

# Paths
CONTENT_INPUT_DIR = Path(__file__).resolve().parent.parent / "content_input"
