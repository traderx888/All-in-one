"""
Trading Dev — Division Manager

Coordinates the three trading sub-systems:
  1. Daytrade Engine   — active intraday strategies
  2. Auto Trading System — automated strategy execution
  3. Signal Alert      — market monitoring & notifications
"""

from __future__ import annotations

from typing import Any

from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus
from src.core.agent_registry import AgentRegistry


class TradingDevDivision(BaseAgent):
    """Division manager for all trading-related pipelines."""

    def __init__(
        self,
        bus: MessageBus,
        registry: AgentRegistry,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            "trading_dev_manager", AgentRole.DIVISION_MANAGER, bus,
            division="trading_dev", config=config,
        )
        self.registry = registry

        # Sub-system researcher entry points
        self._subsystems = {
            "daytrade": "daytrade_researcher",
            "auto_trading": "auto_trading_researcher",
            "signal_alert": "signal_alert_researcher",
        }

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.COMMAND:
            action = message.payload.get("action", "")

            if action == "research":
                # Route research command to the right sub-system
                subsystem = message.payload.get("subsystem", "daytrade")
                target = self._subsystems.get(subsystem)
                if target:
                    await self.send(target, MessageType.COMMAND, message.payload)
                else:
                    self.log.warning("unknown_subsystem", subsystem=subsystem)

            elif action == "start_all":
                for target in self._subsystems.values():
                    await self.send(target, MessageType.COMMAND, {"action": "research"})

            elif action == "get_status":
                agents = self.registry.get_by_division("trading_dev")
                status = [{
                    "name": a.name,
                    "role": a.role.value,
                    "status": a.status.value,
                } for a in agents]
                await self.send(message.sender, MessageType.STATUS, {"trading_dev": status})

        elif message.msg_type == MessageType.TRADE_SIGNAL:
            # Forward trade signals to compliance for risk check
            await self.send("compliance_checker", MessageType.RISK_CHECK, message.payload)

        elif message.msg_type == MessageType.ALERT:
            # Bubble alerts up to secretary
            await self.send("secretary", MessageType.ALERT, {
                "source": "trading_dev",
                "alert": message.payload,
            })
