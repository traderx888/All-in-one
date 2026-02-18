"""Scweet-based scraper using X's GraphQL API.

Scweet uses Twitter/X's internal GraphQL endpoints with account
cookies for authentication. More reliable than Nitter, actively
maintained as of 2026.

Requires: pip install Scweet
Auth: needs X account cookies (auth_token + ct0) in config/cookies.json
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from src.scrapers.base import BaseScraper
from src.models.tweet import Tweet

logger = logging.getLogger(__name__)


class ScweetScraper(BaseScraper):
    """Fetch tweets via Scweet (X GraphQL API).

    This is the recommended backend for 2025-2026 as it uses X's
    internal GraphQL API with cookie-based authentication.
    """

    def __init__(
        self,
        cookies_file: str = "config/cookies.json",
        db_path: str = "data/scweet_state.db",
    ):
        self.cookies_file = cookies_file
        self.db_path = db_path
        self._scweet = None

    def _get_scweet(self):
        """Lazy-init Scweet instance."""
        if self._scweet is None:
            try:
                from Scweet import Scweet
            except ImportError:
                raise ImportError(
                    "Scweet not installed. Run: pip install Scweet"
                )
            self._scweet = Scweet.from_sources(
                db_path=self.db_path,
                cookies_file=self.cookies_file,
                output_format="none",  # We handle storage ourselves
            )
        return self._scweet

    def _parse_graphql_tweet(self, raw: dict, username: str) -> Optional[Tweet]:
        """Convert a Scweet raw GraphQL tweet dict into our Tweet model."""
        try:
            # Scweet returns raw GraphQL objects - extract core fields
            # The structure varies but typically has these nested paths
            legacy = raw.get("legacy", raw)

            tweet_id = str(
                raw.get("rest_id", "")
                or legacy.get("id_str", "")
                or legacy.get("conversation_id_str", "")
            )
            if not tweet_id:
                return None

            text = legacy.get("full_text", "") or legacy.get("text", "")

            # Parse created_at
            created_str = legacy.get("created_at", "")
            try:
                created_at = datetime.strptime(
                    created_str, "%a %b %d %H:%M:%S %z %Y"
                )
            except (ValueError, TypeError):
                created_at = datetime.utcnow()

            # Check retweet
            is_retweet = text.startswith("RT @") or "retweeted_status_result" in raw

            # Check reply
            is_reply = bool(legacy.get("in_reply_to_status_id_str"))

            # Extract media
            media_urls = []
            media_entities = legacy.get("entities", {}).get("media", [])
            for m in media_entities:
                url = m.get("media_url_https") or m.get("media_url", "")
                if url:
                    media_urls.append(url)

            # Also check extended entities
            ext_media = legacy.get("extended_entities", {}).get("media", [])
            for m in ext_media:
                url = m.get("media_url_https") or m.get("media_url", "")
                if url and url not in media_urls:
                    media_urls.append(url)

            return Tweet(
                tweet_id=tweet_id,
                username=username,
                text=text,
                created_at=created_at,
                url=f"https://x.com/{username}/status/{tweet_id}",
                is_retweet=is_retweet,
                is_reply=is_reply,
                media_urls=media_urls,
            )
        except Exception as e:
            logger.warning("Failed to parse tweet from @%s: %s", username, e)
            return None

    async def fetch_tweets(self, username: str, since_id: str = "") -> list[Tweet]:
        """Fetch recent tweets from a user via Scweet."""
        try:
            scweet = self._get_scweet()
        except ImportError as e:
            logger.error(str(e))
            return []

        # Scweet is sync, so run in executor to not block the event loop
        loop = asyncio.get_event_loop()
        try:
            raw_tweets = await loop.run_in_executor(
                None,
                lambda: scweet.profile_tweets(
                    usernames=[username],
                    limit=30,
                    per_profile_limit=30,
                    resume=False,
                    save=False,
                ),
            )
        except Exception as e:
            logger.error("Scweet fetch failed for @%s: %s", username, e)
            return []

        if not raw_tweets:
            logger.info("No tweets returned for @%s", username)
            return []

        tweets = []
        for raw in raw_tweets:
            tweet = self._parse_graphql_tweet(raw, username)
            if tweet is None:
                continue
            # Filter by since_id
            if since_id and tweet.tweet_id <= since_id:
                continue
            tweets.append(tweet)

        # Sort newest first
        tweets.sort(key=lambda t: t.created_at, reverse=True)
        logger.info("Fetched %d tweets for @%s via Scweet", len(tweets), username)
        return tweets

    async def close(self):
        """Scweet manages its own resources."""
        self._scweet = None
