"""CMD (Content Management & Direction) — Shapes content briefs from plans."""

from __future__ import annotations
from typing import Any
from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class CMDAgent(BaseAgent):
    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__("content_cmd", AgentRole.CMD, bus, division="content_dev", config=config)

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.DATA:
            # TODO: Create content briefs and pass to generator
            await self.send("content_generator", MessageType.DATA, {
                "briefs": [],
                "plan": message.payload,
            })
