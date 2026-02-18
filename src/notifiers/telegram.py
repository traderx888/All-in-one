"""Telegram bot notifier."""

import logging
from typing import Optional

import aiohttp

from src.notifiers.base import BaseNotifier
from src.models.tweet import Tweet

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramNotifier(BaseNotifier):
    """Send tweet alerts to a Telegram chat via Bot API."""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def _format_message(self, tweet: Tweet, sentiment: dict = None) -> str:
        sector = tweet.sector.upper() if tweet.sector else "GENERAL"
        lines = [
            f"🔔 <b>[{sector}]</b> New tweet from <b>@{tweet.username}</b>",
        ]
        if sentiment and sentiment.get("label"):
            emoji = sentiment.get("emoji", "")
            label = sentiment["label"]
            score = sentiment.get("score", 0)
            lines.append(f"{emoji} Sentiment: <b>{label}</b> ({score:.0%})")
        lines.extend([
            "",
            tweet.text,
            "",
            f'<a href="{tweet.tweet_link}">View on X</a>',
        ])
        return "\n".join(lines)

    async def send(self, tweet: Tweet, sentiment: dict = None) -> bool:
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram not configured (missing token or chat_id)")
            return False

        session = await self._get_session()
        url = TELEGRAM_API.format(token=self.bot_token)
        payload = {
            "chat_id": self.chat_id,
            "text": self._format_message(tweet, sentiment),
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }

        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    logger.debug("Telegram notification sent for tweet %s", tweet.tweet_id)
                    return True
                body = await resp.text()
                logger.error("Telegram API error %d: %s", resp.status, body[:200])
                return False
        except Exception as e:
            logger.error("Telegram send failed: %s", e)
            return False

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
