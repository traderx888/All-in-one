"""Core monitoring engine - orchestrates scraping, storage, and notifications."""

import asyncio
import logging
from datetime import datetime

from src.models.account import Account
from src.models.database import Database
from src.models.tweet import Tweet
from src.scrapers.base import BaseScraper
from src.notifiers.base import BaseNotifier

logger = logging.getLogger(__name__)


class MonitorEngine:
    """Coordinates fetching tweets, deduplicating, and sending notifications."""

    def __init__(
        self,
        scraper: BaseScraper,
        database: Database,
        notifiers: list[BaseNotifier],
    ):
        self.scraper = scraper
        self.db = database
        self.notifiers = notifiers
        self._running = False

    async def check_account(self, account: Account) -> list[Tweet]:
        """Fetch new tweets for a single account and notify."""
        username = account.username
        since_id = self.db.get_last_tweet_id(username) or ""

        try:
            tweets = await self.scraper.fetch_tweets(username, since_id=since_id)
        except Exception as e:
            logger.error("Failed to fetch @%s: %s", username, e)
            return []

        if not tweets:
            self.db.update_fetch_state(username, since_id)
            return []

        # Tag tweets with sector info
        for tweet in tweets:
            tweet.sector = ", ".join(account.sectors) if account.sectors else ""

        # Save to database (returns only new tweets)
        new_tweets = self.db.save_tweets(tweets)

        if new_tweets:
            # Update fetch state with newest tweet ID
            newest_id = max(t.tweet_id for t in new_tweets)
            self.db.update_fetch_state(username, newest_id)

            # Send notifications for each new tweet
            for tweet in new_tweets:
                await self._notify(tweet)

            logger.info(
                "Found %d new tweets from @%s (sectors: %s)",
                len(new_tweets),
                username,
                ", ".join(account.sectors),
            )
        else:
            self.db.update_fetch_state(username, since_id)

        return new_tweets

    async def check_accounts(self, accounts: list[Account]) -> list[Tweet]:
        """Check multiple accounts sequentially with a small delay between each."""
        all_new = []
        for account in accounts:
            new_tweets = await self.check_account(account)
            all_new.extend(new_tweets)
            # Small delay to avoid rate limiting
            await asyncio.sleep(1)
        return all_new

    async def _notify(self, tweet: Tweet):
        """Send a tweet notification to all configured channels."""
        for notifier in self.notifiers:
            try:
                await notifier.send(tweet)
            except Exception as e:
                logger.error(
                    "Notifier %s failed for tweet %s: %s",
                    type(notifier).__name__, tweet.tweet_id, e,
                )

    async def run_once(self, accounts: list[Account]) -> list[Tweet]:
        """Run a single check cycle for all accounts."""
        logger.info(
            "Starting check cycle for %d accounts at %s",
            len(accounts), datetime.utcnow().strftime("%H:%M:%S"),
        )
        return await self.check_accounts(accounts)

    async def close(self):
        """Clean up all resources."""
        await self.scraper.close()
        for notifier in self.notifiers:
            await notifier.close()
        self.db.close()
