"""
MasterArchitect — Zone ARD

Oversees system architecture decisions and agent configuration.
  - Manages which divisions and pipelines are active
  - Handles dynamic agent creation/teardown
  - Provides configuration management across the system
"""

from __future__ import annotations

from typing import Any

from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus
from src.core.agent_registry import AgentRegistry


class MasterArchitect(BaseAgent):
    """Configuration and architecture overseer."""

    def __init__(
        self,
        bus: MessageBus,
        registry: AgentRegistry,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            "master_architect", AgentRole.MASTER_ARCHITECT, bus,
            division="management_hub", config=config,
        )
        self.registry = registry
        self._system_config: dict[str, Any] = config or {}

    async def handle_message(self, message: Message) -> None:
        action = message.payload.get("action", "")

        if action == "get_architecture":
            summary = self.registry.summary()
            await self.send(
                message.sender,
                MessageType.RESULT,
                {"architecture": summary, "config": self._system_config},
            )

        elif action == "update_config":
            key = message.payload.get("key", "")
            value = message.payload.get("value")
            if key:
                self._system_config[key] = value
                self.log.info("config_updated", key=key)
                # Broadcast config change
                await self.broadcast(
                    MessageType.STATUS,
                    {"event": "config_changed", "key": key, "value": value},
                )

        elif action == "get_config":
            key = message.payload.get("key", "")
            value = self._system_config.get(key)
            await self.send(
                message.sender,
                MessageType.RESULT,
                {"key": key, "value": value},
            )
