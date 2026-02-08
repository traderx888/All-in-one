"""
Content Dev — Division Manager

Coordinates content creation and distribution pipelines:
  - Content Pilot → TrafficMonitor → DataAnalyst
  - Booster Chain: KPI → Campaign
  - Content Chain: PA → CMD → Generator → ArticleKeeper
"""

from __future__ import annotations

from typing import Any

from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus
from src.core.agent_registry import AgentRegistry


class ContentDevDivision(BaseAgent):
    """Division manager for content development pipelines."""

    def __init__(
        self,
        bus: MessageBus,
        registry: AgentRegistry,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            "content_dev_manager", AgentRole.DIVISION_MANAGER, bus,
            division="content_dev", config=config,
        )
        self.registry = registry

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.COMMAND:
            action = message.payload.get("action", "")

            if action == "get_status":
                agents = self.registry.get_by_division("content_dev")
                status = [{"name": a.name, "status": a.status.value} for a in agents]
                await self.send(message.sender, MessageType.STATUS, {"content_dev": status})

            elif action == "create_content":
                await self.send("content_pa", MessageType.COMMAND, message.payload)

            elif action == "boost":
                await self.send("content_kpi", MessageType.COMMAND, message.payload)
