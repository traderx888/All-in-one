"""LINE Notify notifier."""

import logging
from typing import Optional

import aiohttp

from src.notifiers.base import BaseNotifier
from src.models.tweet import Tweet

logger = logging.getLogger(__name__)

LINE_NOTIFY_API = "https://notify-api.line.me/api/notify"


class LineNotifier(BaseNotifier):
    """Send tweet alerts via LINE Notify."""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
        return self.session

    def _format_message(self, tweet: Tweet, sentiment: dict = None) -> str:
        sector = tweet.sector.upper() if tweet.sector else "GENERAL"
        lines = [f"\n[{sector}] @{tweet.username}"]
        if sentiment and sentiment.get("label"):
            emoji = sentiment.get("emoji", "")
            label = sentiment["label"]
            score = sentiment.get("score", 0)
            lines.append(f"{emoji} {label} ({score:.0%})")
        lines.extend([tweet.text, tweet.tweet_link])
        return "\n".join(lines)

    async def send(self, tweet: Tweet, sentiment: dict = None) -> bool:
        if not self.access_token:
            logger.warning("LINE Notify token not configured")
            return False

        session = await self._get_session()
        payload = {"message": self._format_message(tweet, sentiment)}

        try:
            async with session.post(LINE_NOTIFY_API, data=payload) as resp:
                if resp.status == 200:
                    logger.debug("LINE notification sent for tweet %s", tweet.tweet_id)
                    return True
                body = await resp.text()
                logger.error("LINE API error %d: %s", resp.status, body[:200])
                return False
        except Exception as e:
            logger.error("LINE send failed: %s", e)
            return False

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
