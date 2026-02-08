"""
Pipeline: the Researcher → Foreman → Workers pattern.

This is the standard execution pattern used across Trading Dev and Product Dev.
  - Researcher: gathers data, does analysis
  - Foreman:    receives research, creates work plans, assigns to workers
  - Workers:    execute tasks (e.g., place orders, generate content)
"""

from __future__ import annotations

from typing import Any

from .base_agent import BaseAgent, AgentRole, AgentStatus
from .message import Message, MessageBus, MessageType


class ResearcherAgent(BaseAgent):
    """
    Gathers and analyzes data, then passes findings to the Foreman.
    Subclass this and override `research()` with domain-specific logic.
    """

    def __init__(
        self,
        name: str,
        bus: MessageBus,
        foreman_name: str,
        division: str = "",
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, AgentRole.RESEARCHER, bus, division, config)
        self.foreman_name = foreman_name

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.COMMAND:
            command = message.payload.get("action", "")
            if command == "research":
                self.status = AgentStatus.BUSY
                result = await self.research(message.payload)
                await self.send(
                    self.foreman_name,
                    MessageType.DATA,
                    {"research": result, "source_command": message.payload},
                )
                self.status = AgentStatus.RUNNING

    async def research(self, params: dict[str, Any]) -> dict[str, Any]:
        """Override with domain-specific research logic."""
        self.log.warning("research_not_implemented")
        return {}


class ForemanAgent(BaseAgent):
    """
    Receives research data, creates a work plan, and delegates tasks to Workers.
    Subclass this and override `plan()`.
    """

    def __init__(
        self,
        name: str,
        bus: MessageBus,
        worker_names: list[str],
        division: str = "",
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, AgentRole.FOREMAN, bus, division, config)
        self.worker_names = worker_names
        self._pending_tasks: dict[str, dict] = {}

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.DATA:
            # Research results arrived → plan and delegate
            tasks = await self.plan(message.payload)
            await self._delegate(tasks)

        elif message.msg_type == MessageType.TASK_COMPLETE:
            task_id = message.payload.get("task_id", "")
            self._pending_tasks.pop(task_id, None)
            self.log.info("task_completed", task_id=task_id, worker=message.sender)
            await self.on_task_complete(message.payload)

        elif message.msg_type == MessageType.TASK_FAILED:
            task_id = message.payload.get("task_id", "")
            self.log.error("task_failed", task_id=task_id, worker=message.sender)
            await self.on_task_failed(message.payload)

    async def plan(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Override: turn research data into a list of task dicts."""
        self.log.warning("plan_not_implemented")
        return []

    async def on_task_complete(self, result: dict[str, Any]) -> None:
        """Override: handle a completed task from a worker."""
        pass

    async def on_task_failed(self, result: dict[str, Any]) -> None:
        """Override: handle a failed task."""
        pass

    async def _delegate(self, tasks: list[dict[str, Any]]) -> None:
        """Round-robin assign tasks to available workers."""
        for i, task in enumerate(tasks):
            worker = self.worker_names[i % len(self.worker_names)]
            task_id = f"{self.name}_{i}"
            task["task_id"] = task_id
            self._pending_tasks[task_id] = task
            await self.send(worker, MessageType.TASK_ASSIGN, task)
            self.log.info("task_assigned", task_id=task_id, worker=worker)


class WorkerAgent(BaseAgent):
    """
    Executes assigned tasks and reports back to Foreman.
    Subclass this and override `execute()`.
    """

    def __init__(
        self,
        name: str,
        bus: MessageBus,
        foreman_name: str,
        division: str = "",
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, AgentRole.WORKER, bus, division, config)
        self.foreman_name = foreman_name

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.TASK_ASSIGN:
            self.status = AgentStatus.BUSY
            task_id = message.payload.get("task_id", "unknown")
            try:
                result = await self.execute(message.payload)
                await self.send(
                    self.foreman_name,
                    MessageType.TASK_COMPLETE,
                    {"task_id": task_id, "result": result},
                )
            except Exception as e:
                await self.send(
                    self.foreman_name,
                    MessageType.TASK_FAILED,
                    {"task_id": task_id, "error": str(e)},
                )
            finally:
                self.status = AgentStatus.RUNNING

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Override with task execution logic."""
        self.log.warning("execute_not_implemented")
        return {}
