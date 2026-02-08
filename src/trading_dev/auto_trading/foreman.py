"""
Auto Trading System — Foreman

Receives strategy evaluations and creates action plans.
  - Decides which strategies to start, stop, or rebalance
  - Manages strategy lifecycle
  - Delegates execution to workers
"""

from __future__ import annotations

from typing import Any

from src.core.message import MessageBus, MessageType
from src.core.pipeline import ForemanAgent


class AutoTradingForeman(ForemanAgent):
    """Plans and manages automated strategy lifecycle."""

    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        worker_names = config.get("worker_names", ["auto_trading_worker_1"]) if config else ["auto_trading_worker_1"]
        super().__init__(
            name="auto_trading_foreman",
            bus=bus,
            worker_names=worker_names,
            division="trading_dev",
            config=config,
        )

    async def plan(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Create action tasks based on strategy evaluations."""
        research = data.get("research", {})
        evaluations = research.get("evaluations", [])
        tasks = []

        for ev in evaluations:
            if ev.get("needs_action") and ev.get("recommended_action"):
                tasks.append({
                    "action": ev["recommended_action"],
                    "strategy_id": ev["strategy_id"],
                    "strategy_name": ev["name"],
                    "current_pnl": ev.get("pnl", 0),
                    "current_drawdown": ev.get("drawdown", 0),
                })

        self.log.info("auto_plan_created", tasks=len(tasks))
        return tasks

    async def on_task_complete(self, result: dict[str, Any]) -> None:
        await self.send("database_checker", MessageType.COMMAND, {
            "action": "insert",
            "table": "trades",
            "record": result,
        })
