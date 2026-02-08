"""
Daytrade Engine — Workers

Execute trade orders assigned by the Foreman.
  - Submits orders through the exchange connector
  - Monitors fill status
  - Reports execution results back to Foreman
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.core.message import MessageBus, MessageType
from src.core.pipeline import WorkerAgent


class DaytradeWorker(WorkerAgent):
    """Executes individual trade orders on the exchange."""

    def __init__(
        self,
        name: str,
        bus: MessageBus,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            name=name,
            bus=bus,
            foreman_name="daytrade_foreman",
            division="trading_dev",
            config=config,
        )
        self.mode = config.get("mode", "paper") if config else "paper"

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a trade order.

        TODO: Integrate with ccxt exchange connector.
        Currently simulates paper trading execution.
        """
        symbol = task.get("symbol", "")
        side = task.get("side", "")
        entry = task.get("entry_price", 0)

        self.log.info("executing_trade", symbol=symbol, side=side, mode=self.mode)

        if self.mode == "paper":
            # Paper trade simulation
            result = {
                "symbol": symbol,
                "side": side,
                "entry_price": entry,
                "filled_price": entry,  # simulated fill at entry
                "stop_loss": task.get("stop_loss", 0),
                "take_profit": task.get("take_profit", 0),
                "status": "filled",
                "mode": "paper",
                "executed_at": datetime.now(timezone.utc).isoformat(),
            }
        else:
            # Live trade execution (placeholder)
            # order = await exchange.create_order(symbol, 'limit', side, amount, entry)
            result = {
                "symbol": symbol,
                "side": side,
                "status": "not_implemented",
                "mode": "live",
            }

        # Notify compliance of the fill
        await self.send("compliance_checker", MessageType.ORDER_FILLED, result)

        self.log.info("trade_executed", result=result)
        return result
