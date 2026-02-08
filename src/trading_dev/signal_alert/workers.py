"""
Signal Alert — Workers

Deliver alerts through various notification channels.
  - Console output (rich formatting)
  - Telegram messages
  - Future: Discord, email, webhook
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.core.message import MessageBus
from src.core.pipeline import WorkerAgent


class SignalWorker(WorkerAgent):
    """Delivers alert notifications to configured channels."""

    def __init__(
        self,
        name: str,
        bus: MessageBus,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            name=name,
            bus=bus,
            foreman_name="signal_alert_foreman",
            division="trading_dev",
            config=config,
        )

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Deliver an alert through the specified channel."""
        channel = task.get("channel", "console")
        alert = task.get("alert", {})

        self.log.info("delivering_alert", channel=channel, alert_type=alert.get("alert_type"))

        if channel == "console":
            await self._send_console(alert)
        elif channel == "telegram":
            await self._send_telegram(alert)
        else:
            self.log.warning("unknown_channel", channel=channel)

        return {
            "channel": channel,
            "alert": alert,
            "delivered": True,
            "delivered_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _send_console(self, alert: dict[str, Any]) -> None:
        """Print alert to console with rich formatting."""
        severity = alert.get("severity", "info").upper()
        symbol = alert.get("symbol", "???")
        alert_type = alert.get("alert_type", "unknown")
        message = alert.get("message", "")
        self.log.info(
            "ALERT",
            severity=severity,
            symbol=symbol,
            type=alert_type,
            message=message,
        )

    async def _send_telegram(self, alert: dict[str, Any]) -> None:
        """
        Send alert via Telegram.

        TODO: Integrate with python-telegram-bot.
        """
        self.log.info("telegram_alert_placeholder", alert=alert)
