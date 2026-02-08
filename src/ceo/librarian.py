"""
Library (Librarian)

Central knowledge store for the multi-agent system. Responsibilities:
  - Stores and retrieves shared data (market context, configs, research)
  - Provides a key-value interface that any agent can query
  - Maintains versioned history of stored items
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class Librarian(BaseAgent):
    """Shared knowledge base accessible by all agents."""

    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__("librarian", AgentRole.LIBRARIAN, bus, division="ceo", config=config)
        self._store: dict[str, Any] = {}
        self._history: list[dict[str, Any]] = []

    async def handle_message(self, message: Message) -> None:
        action = message.payload.get("action", "")

        if action == "store":
            key = message.payload["key"]
            value = message.payload["value"]
            self._store[key] = value
            self._history.append({
                "action": "store",
                "key": key,
                "by": message.sender,
                "at": datetime.now(timezone.utc).isoformat(),
            })
            self.log.info("stored", key=key, by=message.sender)

        elif action == "retrieve":
            key = message.payload["key"]
            value = self._store.get(key)
            await self.send(
                message.sender,
                MessageType.RESULT,
                {"key": key, "value": value, "found": value is not None},
            )

        elif action == "list_keys":
            await self.send(
                message.sender,
                MessageType.RESULT,
                {"keys": list(self._store.keys())},
            )

        elif action == "delete":
            key = message.payload["key"]
            self._store.pop(key, None)
            self.log.info("deleted", key=key, by=message.sender)

    def get(self, key: str, default: Any = None) -> Any:
        """Direct access (for agents in the same process)."""
        return self._store.get(key, default)

    def put(self, key: str, value: Any) -> None:
        """Direct store (for agents in the same process)."""
        self._store[key] = value
