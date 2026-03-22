"""Base specialist agent with its own context window."""

from __future__ import annotations

import anthropic

from .config import Config
from .models import AgentContext, SpecialistRole, Task


class SpecialistAgent:
    """Base class for specialist agents.

    Each specialist runs in its own context window and has a focused system
    prompt defining its role and capabilities.
    """

    role: SpecialistRole
    system_prompt: str = "You are a helpful specialist agent."

    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.context = AgentContext(role=self.role)

    async def execute(self, task: Task) -> str:
        """Execute a task within this specialist's context window."""
        task.mark_in_progress()

        user_prompt = self._build_prompt(task)
        self.context.add_message("user", user_prompt)

        try:
            response = self.client.messages.create(
                model=self.config.specialist_model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=self.context.get_messages(),
            )
            result = response.content[0].text
            self.context.add_message("assistant", result)
            task.mark_completed(result)
            return result
        except Exception as e:
            task.mark_failed(str(e))
            raise

    def _build_prompt(self, task: Task) -> str:
        """Build a prompt from the task and any shared context."""
        parts = [task.description]
        if task.context:
            parts.append("\n--- Shared context ---")
            for key, value in task.context.items():
                parts.append(f"\n[{key}]:\n{value}")
        return "\n".join(parts)
