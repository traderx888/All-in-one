"""Discord webhook notifier."""

import logging
from typing import Optional

import aiohttp

from src.notifiers.base import BaseNotifier
from src.models.tweet import Tweet

logger = logging.getLogger(__name__)


class DiscordNotifier(BaseNotifier):
    """Send tweet alerts to a Discord channel via webhook."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def _format_embed(self, tweet: Tweet) -> dict:
        sector = tweet.sector.upper() if tweet.sector else "GENERAL"
        color_map = {
            "semiconductor": 0x3498DB,
            "gold": 0xF1C40F,
            "silver": 0xBDC3C7,
            "crypto": 0x9B59B6,
            "macro": 0x2ECC71,
        }
        color = color_map.get(tweet.sector, 0x95A5A6)

        return {
            "embeds": [
                {
                    "title": f"[{sector}] @{tweet.username}",
                    "description": tweet.text,
                    "url": tweet.tweet_link,
                    "color": color,
                    "timestamp": tweet.created_at.isoformat(),
                    "footer": {"text": f"Tweet ID: {tweet.tweet_id}"},
                }
            ]
        }

    async def send(self, tweet: Tweet) -> bool:
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured")
            return False

        session = await self._get_session()
        payload = self._format_embed(tweet)

        try:
            async with session.post(self.webhook_url, json=payload) as resp:
                if resp.status in (200, 204):
                    logger.debug("Discord notification sent for tweet %s", tweet.tweet_id)
                    return True
                body = await resp.text()
                logger.error("Discord webhook error %d: %s", resp.status, body[:200])
                return False
        except Exception as e:
            logger.error("Discord send failed: %s", e)
            return False

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
