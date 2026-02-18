"""Base notifier interface."""

import abc
from src.models.tweet import Tweet


class BaseNotifier(abc.ABC):
    """Abstract base for notification channels."""

    @abc.abstractmethod
    async def send(self, tweet: Tweet, sentiment: dict = None) -> bool:
        """Send a notification for a new tweet.

        Args:
            tweet: The tweet to notify about.
            sentiment: Optional FinTwitBERT result with keys
                       "label", "score", "emoji".

        Returns True if notification was sent successfully.
        """
        ...

    @abc.abstractmethod
    async def close(self):
        """Clean up resources."""
        ...
