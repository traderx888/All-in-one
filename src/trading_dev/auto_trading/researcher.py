"""
Auto Trading System — Researcher

Monitors automated trading strategies that run continuously.
  - Tracks running bots/strategies and their performance
  - Detects strategy drift or anomalies
  - Evaluates when strategies need rebalancing or shutdown
"""

from __future__ import annotations

from typing import Any

from src.core.message import MessageBus
from src.core.pipeline import ResearcherAgent


class AutoTradingResearcher(ResearcherAgent):
    """Monitors and evaluates automated trading strategies."""

    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__(
            name="auto_trading_researcher",
            bus=bus,
            foreman_name="auto_trading_foreman",
            division="trading_dev",
            config=config,
        )
        self.active_strategies: list[dict[str, Any]] = []

    async def research(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate all running automated strategies.

        TODO: Connect to live strategy monitors, fetch PnL, drawdown,
              Sharpe ratio, and other performance metrics.
        """
        self.log.info("evaluating_strategies", count=len(self.active_strategies))

        evaluations = []
        for strategy in self.active_strategies:
            evaluations.append({
                "strategy_id": strategy.get("id", ""),
                "name": strategy.get("name", ""),
                "status": "running",
                "pnl": 0.0,
                "drawdown": 0.0,
                "sharpe": 0.0,
                "needs_action": False,
                "recommended_action": None,  # "rebalance" | "stop" | None
            })

        return {
            "evaluations": evaluations,
            "total_strategies": len(self.active_strategies),
        }
