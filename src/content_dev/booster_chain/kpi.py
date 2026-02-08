"""KPI Agent — Tracks and evaluates content KPIs, then triggers campaigns."""

from __future__ import annotations
from typing import Any
from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class KPIAgent(BaseAgent):
    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__("content_kpi", AgentRole.KPI, bus, division="content_dev", config=config)

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.COMMAND:
            # TODO: Evaluate KPIs and trigger campaign if thresholds met
            await self.send("content_campaign", MessageType.COMMAND, {
                "action": "launch",
                "kpi_data": message.payload,
            })
