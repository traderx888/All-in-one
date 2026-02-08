"""
Product Dev — Division Manager

Coordinates product development pipelines:
  1. Article_RSS   — RSS feed research & content curation
  2. PolyMarket    — Prediction market analysis
  3. Telegram Bot  — Bot development & management
"""

from __future__ import annotations

from typing import Any

from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus
from src.core.agent_registry import AgentRegistry


class ProductDevDivision(BaseAgent):
    """Division manager for product development pipelines."""

    def __init__(
        self,
        bus: MessageBus,
        registry: AgentRegistry,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            "product_dev_manager", AgentRole.DIVISION_MANAGER, bus,
            division="product_dev", config=config,
        )
        self.registry = registry
        self._subsystems = {
            "article_rss": "article_rss_researcher",
            "polymarket": "polymarket_researcher",
            "telegram_bot": "telegram_bot_researcher",
        }

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.COMMAND:
            action = message.payload.get("action", "")
            if action == "research":
                subsystem = message.payload.get("subsystem", "")
                target = self._subsystems.get(subsystem)
                if target:
                    await self.send(target, MessageType.COMMAND, message.payload)

            elif action == "get_status":
                agents = self.registry.get_by_division("product_dev")
                status = [{"name": a.name, "status": a.status.value} for a in agents]
                await self.send(message.sender, MessageType.STATUS, {"product_dev": status})
