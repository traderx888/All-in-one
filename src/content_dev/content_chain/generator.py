"""Generator — Produces content from briefs and passes to ArticleKeeper."""

from __future__ import annotations
from typing import Any
from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class GeneratorAgent(BaseAgent):
    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__("content_generator", AgentRole.GENERATOR, bus, division="content_dev", config=config)

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.DATA:
            # TODO: Generate content from briefs
            await self.send("article_keeper", MessageType.DATA, {
                "articles": [],
                "briefs": message.payload.get("briefs", []),
            })
