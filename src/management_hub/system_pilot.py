"""
SystemPilot — Zone ARD

Monitors the overall health of the agent system.
  - Periodic heartbeat checks on all agents
  - Restarts failed agents
  - Provides a system-wide dashboard / status view
"""

from __future__ import annotations

import asyncio
from typing import Any

from src.core import BaseAgent, AgentRole, AgentStatus, MessageType, Message, MessageBus
from src.core.agent_registry import AgentRegistry


class SystemPilot(BaseAgent):
    """System health monitor and watchdog."""

    def __init__(
        self,
        bus: MessageBus,
        registry: AgentRegistry,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            "system_pilot", AgentRole.SYSTEM_PILOT, bus,
            division="management_hub", config=config,
        )
        self.registry = registry
        self.heartbeat_interval = config.get("heartbeat_interval", 30) if config else 30
        self._heartbeat_task: asyncio.Task | None = None

    async def on_start(self) -> None:
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def on_stop(self) -> None:
        if self._heartbeat_task:
            self._heartbeat_task.cancel()

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.COMMAND:
            action = message.payload.get("action", "")
            if action == "get_status":
                summary = self.registry.summary()
                await self.send(message.sender, MessageType.STATUS, summary)
            elif action == "restart_agent":
                agent_name = message.payload.get("agent_name", "")
                await self._restart_agent(agent_name)

        elif message.msg_type == MessageType.HEARTBEAT:
            pass  # agent is alive, noted

    async def _heartbeat_loop(self) -> None:
        """Periodically check agent health."""
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            for agent in self.registry.get_all():
                if agent.name == self.name:
                    continue
                if agent.status == AgentStatus.ERROR:
                    self.log.warning("agent_unhealthy", agent=agent.name)
                    await self.send(
                        "secretary",
                        MessageType.ALERT,
                        {"alert": f"Agent '{agent.name}' is in ERROR state"},
                    )

    async def _restart_agent(self, agent_name: str) -> None:
        agent = self.registry.get(agent_name)
        if agent:
            await agent.stop()
            await agent.start()
            self.log.info("agent_restarted", agent=agent_name)
