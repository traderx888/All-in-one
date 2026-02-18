"""Scheduling logic for periodic tweet monitoring."""

import asyncio
import logging
import signal
from datetime import datetime

from src.models.account import Account
from src.monitor.engine import MonitorEngine

logger = logging.getLogger(__name__)


class MonitorScheduler:
    """Run monitoring loops at different intervals based on account priority."""

    def __init__(
        self,
        engine: MonitorEngine,
        accounts: dict[str, Account],
        high_interval: int = 120,
        medium_interval: int = 300,
        low_interval: int = 900,
    ):
        self.engine = engine
        self.accounts = accounts
        self.high_interval = high_interval
        self.medium_interval = medium_interval
        self.low_interval = low_interval
        self._running = False
        self._tasks: list[asyncio.Task] = []

    def _group_by_priority(self) -> dict[str, list[Account]]:
        groups: dict[str, list[Account]] = {"high": [], "medium": [], "low": []}
        for account in self.accounts.values():
            pri = account.priority if account.priority in groups else "medium"
            groups[pri].append(account)
        return groups

    async def _poll_loop(self, accounts: list[Account], interval: int, label: str):
        """Continuous polling loop for a priority group."""
        if not accounts:
            return

        usernames = ", ".join(f"@{a.username}" for a in accounts)
        logger.info(
            "[%s] Monitoring %d accounts every %ds: %s",
            label, len(accounts), interval, usernames,
        )

        while self._running:
            try:
                new_tweets = await self.engine.run_once(accounts)
                if new_tweets:
                    logger.info(
                        "[%s] Cycle complete: %d new tweets found",
                        label, len(new_tweets),
                    )
            except Exception as e:
                logger.error("[%s] Cycle error: %s", label, e)

            await asyncio.sleep(interval)

    async def start(self):
        """Start all polling loops."""
        self._running = True
        groups = self._group_by_priority()

        total = sum(len(g) for g in groups.values())
        logger.info(
            "Starting scheduler: %d accounts "
            "(high=%d, medium=%d, low=%d)",
            total, len(groups["high"]), len(groups["medium"]), len(groups["low"]),
        )

        # Launch concurrent polling loops per priority
        if groups["high"]:
            self._tasks.append(
                asyncio.create_task(
                    self._poll_loop(groups["high"], self.high_interval, "HIGH")
                )
            )
        if groups["medium"]:
            self._tasks.append(
                asyncio.create_task(
                    self._poll_loop(groups["medium"], self.medium_interval, "MEDIUM")
                )
            )
        if groups["low"]:
            self._tasks.append(
                asyncio.create_task(
                    self._poll_loop(groups["low"], self.low_interval, "LOW")
                )
            )

        if not self._tasks:
            logger.warning("No accounts to monitor!")
            return

        # Wait for all tasks (they run forever until stopped)
        try:
            await asyncio.gather(*self._tasks)
        except asyncio.CancelledError:
            logger.info("Scheduler stopped.")

    async def stop(self):
        """Gracefully stop all polling loops."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        await self.engine.close()
        logger.info("Scheduler shut down cleanly.")
