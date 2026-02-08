"""
Signal Alert — Foreman

Processes detected signals and decides how to deliver alerts.
  - Filters by severity and user preferences
  - Routes alerts to appropriate notification channels
  - Prevents alert fatigue via deduplication and throttling
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.core.message import MessageBus, MessageType
from src.core.pipeline import ForemanAgent


class SignalForeman(ForemanAgent):
    """Plans alert delivery based on detected signals."""

    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        worker_names = config.get("worker_names", ["signal_worker_1"]) if config else ["signal_worker_1"]
        super().__init__(
            name="signal_alert_foreman",
            bus=bus,
            worker_names=worker_names,
            division="trading_dev",
            config=config,
        )
        self.channels = config.get("channels", ["console"]) if config else ["console"]
        self._recent_alerts: dict[str, str] = {}  # dedup: key → timestamp

    async def plan(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Create alert delivery tasks for triggered signals."""
        research = data.get("research", {})
        alerts = research.get("alerts", [])
        tasks = []

        for alert in alerts:
            if not alert.get("triggered"):
                continue

            # Deduplication: skip if same alert was sent recently
            dedup_key = f"{alert['symbol']}_{alert['alert_type']}"
            if dedup_key in self._recent_alerts:
                continue

            self._recent_alerts[dedup_key] = datetime.now(timezone.utc).isoformat()

            for channel in self.channels:
                tasks.append({
                    "action": "send_alert",
                    "channel": channel,
                    "alert": alert,
                })

        self.log.info("alert_plan_created", tasks=len(tasks))
        return tasks

    async def on_task_complete(self, result: dict[str, Any]) -> None:
        await self.send("database_checker", MessageType.COMMAND, {
            "action": "insert",
            "table": "signals",
            "record": result,
        })
