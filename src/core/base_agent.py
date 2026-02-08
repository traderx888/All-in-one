"""
Base agent class that all agents inherit from.

Every agent in the system (CEO Secretary, Foreman, Worker, etc.)
extends BaseAgent and implements its handle_message() method.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

import structlog

from .message import Message, MessageBus, MessageType


class AgentRole(str, Enum):
    """Standard roles matching the architecture diagram."""
    # CEO layer
    SECRETARY = "secretary"
    LIBRARIAN = "librarian"

    # Management Hub
    COMPLIANCE_CHECKER = "compliance_checker"
    SYSTEM_PILOT = "system_pilot"
    TASK_MANAGER = "task_manager"
    DATABASE_CHECKER = "database_checker"
    MASTER_ARCHITECT = "master_architect"

    # Pipeline roles (used across divisions)
    RESEARCHER = "researcher"
    FOREMAN = "foreman"
    WORKER = "worker"

    # Content Dev specific
    CONTENT_PILOT = "content_pilot"
    TRAFFIC_MONITOR = "traffic_monitor"
    DATA_ANALYST = "data_analyst"
    KPI = "kpi"
    CAMPAIGN = "campaign"
    PA = "pa"
    CMD = "cmd"
    GENERATOR = "generator"
    ARTICLE_KEEPER = "article_keeper"

    # Division manager
    DIVISION_MANAGER = "division_manager"


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"


class BaseAgent(ABC):
    """
    Abstract base for every agent in the system.

    Lifecycle:
        1. __init__  → agent created, not yet connected
        2. start()   → registers on message bus, begins listening
        3. handle_message() → processes incoming messages (override this)
        4. stop()    → unregisters, cleans up
    """

    def __init__(
        self,
        name: str,
        role: AgentRole,
        bus: MessageBus,
        division: str = "",
        config: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.role = role
        self.bus = bus
        self.division = division
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.log = structlog.get_logger().bind(agent=name, role=role.value)

    async def start(self) -> None:
        """Register on the bus and start running."""
        self.bus.subscribe(self.name, self._on_message)
        self.status = AgentStatus.RUNNING
        self.log.info("agent_started")
        await self.on_start()

    async def stop(self) -> None:
        """Unregister and clean up."""
        self.bus.unsubscribe(self.name)
        self.status = AgentStatus.STOPPED
        await self.on_stop()
        self.log.info("agent_stopped")

    async def send(
        self,
        receiver: str,
        msg_type: MessageType,
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Send a message to another agent."""
        msg = Message(
            msg_type=msg_type,
            sender=self.name,
            receiver=receiver,
            payload=payload or {},
        )
        await self.bus.publish(msg)

    async def broadcast(
        self, msg_type: MessageType, payload: dict[str, Any] | None = None
    ) -> None:
        """Broadcast a message to all agents."""
        await self.send("*", msg_type, payload)

    # --- Internal ---

    async def _on_message(self, message: Message) -> None:
        """Wrapper that catches errors in message handling."""
        try:
            await self.handle_message(message)
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.log.error("handle_message_failed", error=str(e), msg_type=message.msg_type)
            await self.send(
                message.sender,
                MessageType.ERROR,
                {"error": str(e), "original_msg_id": message.msg_id},
            )

    # --- Override these ---

    @abstractmethod
    async def handle_message(self, message: Message) -> None:
        """Process an incoming message. Must be implemented by subclasses."""
        ...

    async def on_start(self) -> None:
        """Called after agent registers on the bus. Override for init logic."""
        pass

    async def on_stop(self) -> None:
        """Called before agent unregisters. Override for cleanup."""
        pass
