"""Content Pilot — Oversees content strategy and directs traffic analysis."""

from __future__ import annotations
from typing import Any
from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class ContentPilot(BaseAgent):
    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__("content_pilot", AgentRole.CONTENT_PILOT, bus, division="content_dev", config=config)

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.COMMAND:
            action = message.payload.get("action", "")
            if action == "analyze_traffic":
                await self.send("traffic_monitor", MessageType.COMMAND, message.payload)
            elif action == "get_insights":
                await self.send("data_analyst", MessageType.COMMAND, message.payload)
