"""
Message system for inter-agent communication.

Agents communicate exclusively through Message objects routed by the MessageBus.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine


class MessageType(str, Enum):
    # Control
    COMMAND = "command"
    STATUS = "status"
    HEARTBEAT = "heartbeat"

    # Data flow
    DATA = "data"
    SIGNAL = "signal"
    RESULT = "result"
    ERROR = "error"

    # Task management
    TASK_ASSIGN = "task_assign"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"

    # Trading specific
    TRADE_SIGNAL = "trade_signal"
    ORDER_REQUEST = "order_request"
    ORDER_FILLED = "order_filled"
    RISK_CHECK = "risk_check"
    RISK_APPROVED = "risk_approved"
    RISK_REJECTED = "risk_rejected"
    ALERT = "alert"


@dataclass
class Message:
    """A message passed between agents."""
    msg_type: MessageType
    sender: str
    receiver: str              # agent name or "*" for broadcast
    payload: dict[str, Any] = field(default_factory=dict)
    msg_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str | None = None  # to track request/response chains

    def reply(self, msg_type: MessageType, payload: dict[str, Any]) -> Message:
        """Create a reply message back to the sender."""
        return Message(
            msg_type=msg_type,
            sender=self.receiver,
            receiver=self.sender,
            payload=payload,
            correlation_id=self.msg_id,
        )


# Type alias for message handler callbacks
MessageHandler = Callable[[Message], Coroutine[Any, Any, None]]


class MessageBus:
    """
    Central message bus that routes messages between agents.
    Supports direct messaging and topic-based pub/sub.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[MessageHandler]] = {}   # agent_name → handlers
        self._topic_subs: dict[MessageType, list[MessageHandler]] = {}
        self._queue: asyncio.Queue[Message] = asyncio.Queue()
        self._running = False

    def subscribe(self, agent_name: str, handler: MessageHandler) -> None:
        """Subscribe an agent to receive direct messages."""
        self._subscribers.setdefault(agent_name, []).append(handler)

    def subscribe_topic(self, msg_type: MessageType, handler: MessageHandler) -> None:
        """Subscribe to all messages of a given type."""
        self._topic_subs.setdefault(msg_type, []).append(handler)

    def unsubscribe(self, agent_name: str) -> None:
        """Remove all subscriptions for an agent."""
        self._subscribers.pop(agent_name, None)

    async def publish(self, message: Message) -> None:
        """Put a message on the bus for delivery."""
        await self._queue.put(message)

    async def start(self) -> None:
        """Start the message routing loop."""
        self._running = True
        while self._running:
            try:
                message = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            # Route to direct subscribers
            if message.receiver == "*":
                # Broadcast to all
                for handlers in self._subscribers.values():
                    for handler in handlers:
                        asyncio.create_task(self._safe_call(handler, message))
            else:
                for handler in self._subscribers.get(message.receiver, []):
                    asyncio.create_task(self._safe_call(handler, message))

            # Route to topic subscribers
            for handler in self._topic_subs.get(message.msg_type, []):
                asyncio.create_task(self._safe_call(handler, message))

            self._queue.task_done()

    async def stop(self) -> None:
        self._running = False

    @staticmethod
    async def _safe_call(handler: MessageHandler, message: Message) -> None:
        try:
            await handler(message)
        except Exception as e:
            import structlog
            log = structlog.get_logger()
            log.error("message_handler_error", handler=handler.__qualname__, error=str(e))
