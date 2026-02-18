"""Nitter RSS-based scraper for Twitter/X content."""

import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional

import aiohttp

from src.scrapers.base import BaseScraper
from src.models.tweet import Tweet

logger = logging.getLogger(__name__)


class NitterScraper(BaseScraper):
    """Fetch tweets via Nitter RSS feeds.

    Nitter provides public RSS feeds for Twitter accounts without
    requiring API authentication. Multiple instances are supported
    with automatic failover.

    Uses stdlib xml.etree for RSS parsing (no external dependency).
    """

    def __init__(
        self,
        instances: list[str] = None,
        timeout: int = 30,
        user_agent: str = "Mozilla/5.0 (compatible; AssetMonitor/1.0)",
    ):
        self.instances = instances or [
            "https://nitter.privacydev.net",
            "https://nitter.poast.org",
            "https://nitter.woodland.cafe",
        ]
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.headers = {"User-Agent": user_agent}
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout, headers=self.headers
            )
        return self.session

    def _parse_tweet_id(self, link: str) -> str:
        """Extract tweet ID from a Nitter/Twitter URL."""
        match = re.search(r"/status/(\d+)", link)
        return match.group(1) if match else ""

    def _parse_rss_xml(self, xml_text: str, username: str) -> list[Tweet]:
        """Parse RSS XML into Tweet objects using stdlib ElementTree."""
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            logger.warning("Failed to parse RSS XML: %s", e)
            return []

        tweets = []
        # RSS items are under <channel><item>
        for item in root.iter("item"):
            link = (item.findtext("link") or "").strip()
            tweet_id = self._parse_tweet_id(link)
            if not tweet_id:
                continue

            # Parse pubDate (RFC 2822 format)
            pub_date_str = item.findtext("pubDate", "").strip()
            try:
                created_at = parsedate_to_datetime(pub_date_str)
            except (ValueError, TypeError):
                created_at = datetime.utcnow()

            # Get title and description
            title = item.findtext("title", "").strip()
            description = item.findtext("description", "").strip()

            # Use title as primary text, fall back to description
            text = title or description
            # Strip HTML tags
            text = re.sub(r"<[^>]+>", "", text).strip()

            # Check if retweet
            is_retweet = text.startswith("RT @") or text.startswith("RT by")

            # Extract media URLs from description HTML
            media_urls = []
            if description:
                img_matches = re.findall(
                    r'src="([^"]+\.(?:jpg|jpeg|png|gif|mp4))"', description
                )
                media_urls = img_matches

            # Convert Nitter URL to X URL
            url = re.sub(
                r"https?://[^/]+/([^/]+)/status/(\d+)",
                r"https://x.com/\1/status/\2",
                link,
            )

            tweets.append(
                Tweet(
                    tweet_id=tweet_id,
                    username=username,
                    text=text,
                    created_at=created_at,
                    url=url,
                    is_retweet=is_retweet,
                    media_urls=media_urls,
                )
            )

        return tweets

    async def fetch_tweets(self, username: str, since_id: str = "") -> list[Tweet]:
        """Fetch tweets via Nitter RSS, trying multiple instances."""
        session = await self._get_session()
        last_error = None

        for instance in self.instances:
            rss_url = f"{instance}/{username}/rss"
            try:
                logger.debug("Fetching RSS: %s", rss_url)
                async with session.get(rss_url) as resp:
                    if resp.status != 200:
                        logger.warning(
                            "Instance %s returned %d for @%s",
                            instance, resp.status, username,
                        )
                        continue
                    body = await resp.text()

                tweets = self._parse_rss_xml(body, username)
                if not tweets:
                    logger.info("No entries from %s for @%s", instance, username)
                    continue

                # Filter by since_id
                if since_id:
                    tweets = [t for t in tweets if t.tweet_id > since_id]

                # Sort newest first
                tweets.sort(key=lambda t: t.created_at, reverse=True)
                logger.info(
                    "Fetched %d tweets for @%s from %s",
                    len(tweets), username, instance,
                )
                return tweets

            except Exception as e:
                last_error = e
                logger.warning(
                    "Instance %s failed for @%s: %s", instance, username, e
                )
                continue

        logger.error(
            "All Nitter instances failed for @%s. Last error: %s",
            username, last_error,
        )
        return []

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
