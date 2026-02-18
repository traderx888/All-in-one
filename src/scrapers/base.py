"""Base scraper interface."""

import abc
from src.models.tweet import Tweet


class BaseScraper(abc.ABC):
    """Abstract base for all Twitter/X scrapers."""

    @abc.abstractmethod
    async def fetch_tweets(self, username: str, since_id: str = "") -> list[Tweet]:
        """Fetch recent tweets from a user.

        Args:
            username: Twitter handle (without @).
            since_id: Only return tweets newer than this ID (optional).

        Returns:
            List of Tweet objects, newest first.
        """
        ...

    @abc.abstractmethod
    async def close(self):
        """Clean up resources."""
        ...
