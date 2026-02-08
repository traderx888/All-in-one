"""
CEO Secretary (Secy)

Acts as the primary interface between the User (CEO) and the rest of the
multi-agent system. Responsibilities:
  - Routes user commands to the correct division / management hub agent
  - Aggregates status reports and presents them to the user
  - Maintains a command log for audit trail
"""

from __future__ import annotations

from typing import Any

from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class Secretary(BaseAgent):
    """Gateway between the human CEO and the agent fleet."""

    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__("secretary", AgentRole.SECRETARY, bus, division="ceo", config=config)
        self._command_log: list[dict[str, Any]] = []

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.COMMAND:
            await self._route_command(message)

        elif message.msg_type == MessageType.STATUS:
            self.log.info("status_report", source=message.sender, data=message.payload)

        elif message.msg_type == MessageType.RESULT:
            self.log.info("result_received", source=message.sender, data=message.payload)

        elif message.msg_type == MessageType.ERROR:
            self.log.error("error_report", source=message.sender, data=message.payload)

        elif message.msg_type == MessageType.ALERT:
            self.log.warning("alert", source=message.sender, data=message.payload)

    async def _route_command(self, message: Message) -> None:
        """Route a CEO command to the appropriate agent or division."""
        target = message.payload.get("target")
        action = message.payload.get("action")

        self._command_log.append({
            "msg_id": message.msg_id,
            "target": target,
            "action": action,
            "timestamp": message.timestamp.isoformat(),
        })

        if target:
            await self.send(target, MessageType.COMMAND, message.payload)
            self.log.info("command_routed", target=target, action=action)
        else:
            # Default: send to task_manager for triage
            await self.send("task_manager", MessageType.COMMAND, message.payload)

    async def submit_command(self, target: str, action: str, **kwargs: Any) -> None:
        """Convenience method for programmatic command submission."""
        payload = {"target": target, "action": action, **kwargs}
        await self.send(self.name, MessageType.COMMAND, payload)

    def get_command_log(self) -> list[dict[str, Any]]:
        return list(self._command_log)
