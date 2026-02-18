"""Twitter API v2 scraper (requires Bearer Token)."""

import logging
import os
from datetime import datetime
from typing import Optional

import aiohttp

from src.scrapers.base import BaseScraper
from src.models.tweet import Tweet

logger = logging.getLogger(__name__)

TWITTER_API_BASE = "https://api.twitter.com/2"


class TwitterAPIScraper(BaseScraper):
    """Fetch tweets using the official Twitter API v2.

    Requires a Bearer Token (set via TWITTER_BEARER_TOKEN env var
    or passed directly). The free tier allows basic read access;
    Basic tier ($100/month) gives higher rate limits.
    """

    def __init__(self, bearer_token: str = "", timeout: int = 30):
        self.bearer_token = bearer_token or os.environ.get("TWITTER_BEARER_TOKEN", "")
        if not self.bearer_token:
            logger.warning(
                "No Twitter Bearer Token configured. "
                "Set TWITTER_BEARER_TOKEN env var or use a different backend."
            )
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={"Authorization": f"Bearer {self.bearer_token}"},
            )
        return self.session

    async def _get_user_id(self, username: str) -> Optional[str]:
        """Resolve username to Twitter user ID."""
        session = await self._get_session()
        url = f"{TWITTER_API_BASE}/users/by/username/{username}"
        async with session.get(url) as resp:
            if resp.status != 200:
                logger.error("Failed to resolve @%s: HTTP %d", username, resp.status)
                return None
            data = await resp.json()
            return data.get("data", {}).get("id")

    async def fetch_tweets(self, username: str, since_id: str = "") -> list[Tweet]:
        """Fetch recent tweets via Twitter API v2."""
        if not self.bearer_token:
            logger.error("Cannot fetch: no Bearer Token configured")
            return []

        session = await self._get_session()
        user_id = await self._get_user_id(username)
        if not user_id:
            return []

        params = {
            "max_results": 20,
            "tweet.fields": "created_at,text,referenced_tweets,attachments",
            "expansions": "attachments.media_keys",
            "media.fields": "url,preview_image_url",
        }
        if since_id:
            params["since_id"] = since_id

        url = f"{TWITTER_API_BASE}/users/{user_id}/tweets"
        try:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logger.error(
                        "API error for @%s: HTTP %d - %s",
                        username, resp.status, body[:200],
                    )
                    return []
                data = await resp.json()
        except Exception as e:
            logger.error("API request failed for @%s: %s", username, e)
            return []

        # Parse media from includes
        media_map = {}
        for media in data.get("includes", {}).get("media", []):
            key = media.get("media_key", "")
            url_val = media.get("url") or media.get("preview_image_url", "")
            if key and url_val:
                media_map[key] = url_val

        tweets = []
        for item in data.get("data", []):
            tweet_id = item["id"]
            text = item.get("text", "")
            created_str = item.get("created_at", "")
            try:
                created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                created_at = datetime.utcnow()

            # Check for retweet
            is_retweet = False
            refs = item.get("referenced_tweets", [])
            if refs:
                is_retweet = any(r.get("type") == "retweeted" for r in refs)

            # Gather media
            media_keys = (
                item.get("attachments", {}).get("media_keys", [])
            )
            media_urls = [media_map[k] for k in media_keys if k in media_map]

            tweets.append(
                Tweet(
                    tweet_id=tweet_id,
                    username=username,
                    text=text,
                    created_at=created_at,
                    url=f"https://x.com/{username}/status/{tweet_id}",
                    is_retweet=is_retweet,
                    media_urls=media_urls,
                )
            )

        tweets.sort(key=lambda t: t.created_at, reverse=True)
        logger.info("Fetched %d tweets for @%s via API", len(tweets), username)
        return tweets

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
