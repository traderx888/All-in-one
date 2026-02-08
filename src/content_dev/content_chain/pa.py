"""PA (Planning Assistant) — First stage: plans content structure and topics."""

from __future__ import annotations
from typing import Any
from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class PAAgent(BaseAgent):
    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__("content_pa", AgentRole.PA, bus, division="content_dev", config=config)

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.COMMAND:
            # TODO: Plan content topics and structure
            await self.send("content_cmd", MessageType.DATA, {
                "content_plan": message.payload,
                "topics": [],
            })
