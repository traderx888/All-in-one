"""Data models for the multi-agent system."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SpecialistRole(Enum):
    ARCHITECT = "architect"
    IMPLEMENTER = "implementer"
    TESTER = "tester"
    REVIEWER = "reviewer"


@dataclass
class Task:
    """A unit of work assigned to a specialist agent."""

    description: str
    role: SpecialistRole
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    status: TaskStatus = TaskStatus.PENDING
    context: dict[str, Any] = field(default_factory=dict)
    result: str | None = None
    error: str | None = None

    def mark_in_progress(self) -> None:
        self.status = TaskStatus.IN_PROGRESS

    def mark_completed(self, result: str) -> None:
        self.status = TaskStatus.COMPLETED
        self.result = result

    def mark_failed(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.error = error


@dataclass
class AgentContext:
    """Isolated context window for a specialist agent."""

    role: SpecialistRole
    messages: list[dict[str, str]] = field(default_factory=list)
    shared_artifacts: dict[str, str] = field(default_factory=dict)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        return list(self.messages)


@dataclass
class OrchestratorPlan:
    """The orchestrator's decomposition of a developer request."""

    original_request: str
    tasks: list[Task] = field(default_factory=list)
    integrated_output: str | None = None

    @property
    def all_completed(self) -> bool:
        return all(t.status == TaskStatus.COMPLETED for t in self.tasks)

    @property
    def any_failed(self) -> bool:
        return any(t.status == TaskStatus.FAILED for t in self.tasks)

    def tasks_for_role(self, role: SpecialistRole) -> list[Task]:
        return [t for t in self.tasks if t.role == role]
