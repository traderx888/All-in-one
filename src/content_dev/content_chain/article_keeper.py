"""ArticleKeeper — Final stage: stores, publishes, and archives content."""

from __future__ import annotations
from typing import Any
from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class ArticleKeeperAgent(BaseAgent):
    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__("article_keeper", AgentRole.ARTICLE_KEEPER, bus, division="content_dev", config=config)
        self._articles: list[dict[str, Any]] = []

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.DATA:
            articles = message.payload.get("articles", [])
            self._articles.extend(articles)
            self.log.info("articles_stored", count=len(articles), total=len(self._articles))
            # Notify division manager
            await self.send("content_dev_manager", MessageType.RESULT, {
                "action": "content_created",
                "count": len(articles),
            })
