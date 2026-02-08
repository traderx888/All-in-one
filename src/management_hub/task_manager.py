"""
NewTaskManager — Zone ARD

Central task coordination hub.
  - Receives tasks from Secretary or other agents
  - Routes tasks to the correct division
  - Tracks task lifecycle (pending → running → done/failed)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskManager(BaseAgent):
    """Routes and tracks tasks across the system."""

    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__(
            "task_manager", AgentRole.TASK_MANAGER, bus,
            division="management_hub", config=config,
        )
        self._tasks: dict[str, dict[str, Any]] = {}

        # Division routing map
        self._division_map: dict[str, str] = {
            "trading": "trading_dev_manager",
            "product": "product_dev_manager",
            "content": "content_dev_manager",
            "compliance": "compliance_checker",
            "system": "system_pilot",
        }

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.COMMAND:
            action = message.payload.get("action", "")

            if action == "create_task":
                task_id = await self._create_task(message.payload, message.sender)
                await self.send(
                    message.sender,
                    MessageType.RESULT,
                    {"task_id": task_id, "status": "created"},
                )

            elif action == "get_tasks":
                await self.send(
                    message.sender,
                    MessageType.RESULT,
                    {"tasks": list(self._tasks.values())},
                )

            elif action == "cancel_task":
                task_id = message.payload.get("task_id", "")
                self._tasks.pop(task_id, None)

            else:
                # Default: treat the command as a new task
                division = message.payload.get("division", "trading")
                target = self._division_map.get(division)
                if target:
                    await self.send(target, MessageType.COMMAND, message.payload)
                else:
                    self.log.warning("unknown_division", division=division)

        elif message.msg_type == MessageType.TASK_COMPLETE:
            task_id = message.payload.get("task_id", "")
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = TaskStatus.COMPLETED.value
                self._tasks[task_id]["completed_at"] = datetime.now(timezone.utc).isoformat()

        elif message.msg_type == MessageType.TASK_FAILED:
            task_id = message.payload.get("task_id", "")
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = TaskStatus.FAILED.value
                self._tasks[task_id]["error"] = message.payload.get("error", "")

    async def _create_task(self, params: dict[str, Any], requester: str) -> str:
        task_id = uuid.uuid4().hex[:8]
        task = {
            "id": task_id,
            "requester": requester,
            "division": params.get("division", "trading"),
            "action": params.get("task_action", ""),
            "params": params,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._tasks[task_id] = task

        # Route to the right division
        target = self._division_map.get(task["division"])
        if target:
            await self.send(target, MessageType.COMMAND, {
                "action": task["action"],
                "task_id": task_id,
                **params,
            })
            task["status"] = TaskStatus.RUNNING.value

        return task_id
