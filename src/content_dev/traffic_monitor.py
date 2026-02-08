"""TrafficMonitor — Monitors content performance and traffic metrics."""

from __future__ import annotations
from typing import Any
from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class TrafficMonitor(BaseAgent):
    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__("traffic_monitor", AgentRole.TRAFFIC_MONITOR, bus, division="content_dev", config=config)

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.COMMAND:
            action = message.payload.get("action", "")
            if action == "analyze_traffic":
                # TODO: Fetch traffic data and pass to DataAnalyst
                await self.send("data_analyst", MessageType.DATA, {
                    "traffic_data": {},
                    "source": "traffic_monitor",
                })
