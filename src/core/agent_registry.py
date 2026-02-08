"""
Agent Registry — tracks all agents in the system.

Provides lookup by name, role, division, and status.
Used by Management Hub agents (TaskManager, SystemPilot) to monitor the fleet.
"""

from __future__ import annotations

from typing import Any

from .base_agent import BaseAgent, AgentRole, AgentStatus


class AgentRegistry:
    """Singleton registry of all active agents."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def unregister(self, name: str) -> None:
        self._agents.pop(name, None)

    def get(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def get_all(self) -> list[BaseAgent]:
        return list(self._agents.values())

    def get_by_role(self, role: AgentRole) -> list[BaseAgent]:
        return [a for a in self._agents.values() if a.role == role]

    def get_by_division(self, division: str) -> list[BaseAgent]:
        return [a for a in self._agents.values() if a.division == division]

    def get_by_status(self, status: AgentStatus) -> list[BaseAgent]:
        return [a for a in self._agents.values() if a.status == status]

    def summary(self) -> dict[str, Any]:
        """Return a status summary of all agents (used by SystemPilot dashboard)."""
        agents = []
        for a in self._agents.values():
            agents.append({
                "name": a.name,
                "role": a.role.value,
                "division": a.division,
                "status": a.status.value,
            })
        return {
            "total": len(agents),
            "running": sum(1 for a in agents if a["status"] == "running"),
            "agents": agents,
        }

    async def start_all(self) -> None:
        for agent in self._agents.values():
            await agent.start()

    async def stop_all(self) -> None:
        for agent in self._agents.values():
            await agent.stop()
