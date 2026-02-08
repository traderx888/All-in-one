"""
Daytrade Engine — Foreman

Receives research signals from the Researcher, filters them,
calculates position sizing, and assigns execution tasks to Workers.
"""

from __future__ import annotations

from typing import Any

from src.core.message import MessageBus, MessageType
from src.core.pipeline import ForemanAgent


class DaytradeForeman(ForemanAgent):
    """Plans and delegates trade execution based on research signals."""

    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        worker_names = config.get("worker_names", ["daytrade_worker_1"]) if config else ["daytrade_worker_1"]
        super().__init__(
            name="daytrade_foreman",
            bus=bus,
            worker_names=worker_names,
            division="trading_dev",
            config=config,
        )
        self.min_confidence = config.get("min_confidence", 0.6) if config else 0.6
        self.risk_per_trade = config.get("risk_per_trade_pct", 1.0) if config else 1.0

    async def plan(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Filter signals and create executable trade tasks."""
        research = data.get("research", {})
        signals = research.get("signals", [])
        tasks = []

        for sig in signals:
            # Only act on actionable signals above confidence threshold
            if sig.get("signal") is None:
                continue
            if sig.get("confidence", 0) < self.min_confidence:
                continue

            task = {
                "action": "execute_trade",
                "symbol": sig["symbol"],
                "side": sig["signal"],       # "buy" or "sell"
                "entry_price": sig["entry_price"],
                "stop_loss": sig["stop_loss"],
                "take_profit": sig["take_profit"],
                "risk_pct": self.risk_per_trade,
                "strategy": sig["strategy"],
                "confidence": sig["confidence"],
            }
            tasks.append(task)

        self.log.info("plan_created", total_signals=len(signals), actionable_tasks=len(tasks))
        return tasks

    async def on_task_complete(self, result: dict[str, Any]) -> None:
        """Notify the division manager and database about completed trades."""
        await self.send("database_checker", MessageType.COMMAND, {
            "action": "insert",
            "table": "trades",
            "record": result,
        })
        await self.send("trading_dev_manager", MessageType.RESULT, {
            "subsystem": "daytrade",
            "result": result,
        })

    async def on_task_failed(self, result: dict[str, Any]) -> None:
        """Alert on failed trade execution."""
        await self.send("trading_dev_manager", MessageType.ALERT, {
            "subsystem": "daytrade",
            "error": result.get("error", "unknown"),
        })
