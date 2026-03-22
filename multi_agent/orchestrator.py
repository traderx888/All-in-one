"""Orchestrator agent: task decomposition, work distribution, result synthesis."""

from __future__ import annotations

import asyncio
import json

import anthropic

from .config import Config
from .models import OrchestratorPlan, SpecialistRole, Task
from .specialist import SpecialistAgent
from .specialists import (
    ArchitectAgent,
    ImplementerAgent,
    ReviewerAgent,
    TesterAgent,
)

DECOMPOSITION_PROMPT = """\
You are an orchestrator agent managing a team of four specialists:
- architect: Architecture and design
- implementer: Implementation and coding
- tester: Testing and validation
- reviewer: Review and documentation

Given the developer's request below, decompose it into concrete tasks for each
specialist. Return a JSON array of tasks, where each task has:
- "role": one of "architect", "implementer", "tester", "reviewer"
- "description": a clear, actionable description of what the specialist should do
- "depends_on": list of role names whose output this task needs (empty list if independent)

Order tasks so that dependencies are respected. Typically:
1. Architect designs first
2. Implementer codes based on the design
3. Tester validates the implementation
4. Reviewer reviews everything and writes docs

Return ONLY valid JSON — no markdown fences, no commentary.

Developer request:
{request}
"""

SYNTHESIS_PROMPT = """\
You are an orchestrator agent. The specialist agents have completed their work.
Synthesize their outputs into a single, coherent integrated response for the
developer. Include the key deliverables from each specialist.

Original request:
{request}

Specialist outputs:
{outputs}

Provide a clear, well-structured integrated response.
"""


class Orchestrator:
    """Central orchestrator that decomposes, distributes, and synthesizes."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config.from_env()
        self.client = anthropic.Anthropic(api_key=self.config.api_key)
        self._specialists: dict[SpecialistRole, SpecialistAgent] = {
            SpecialistRole.ARCHITECT: ArchitectAgent(self.config),
            SpecialistRole.IMPLEMENTER: ImplementerAgent(self.config),
            SpecialistRole.TESTER: TesterAgent(self.config),
            SpecialistRole.REVIEWER: ReviewerAgent(self.config),
        }

    def decompose(self, request: str) -> OrchestratorPlan:
        """Decompose a developer request into specialist tasks."""
        response = self.client.messages.create(
            model=self.config.orchestrator_model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": DECOMPOSITION_PROMPT.format(request=request),
                }
            ],
        )
        raw = response.content[0].text
        task_defs = json.loads(raw)

        plan = OrchestratorPlan(original_request=request)
        for td in task_defs:
            role = SpecialistRole(td["role"])
            plan.tasks.append(
                Task(description=td["description"], role=role)
            )
        return plan

    async def execute_plan(self, plan: OrchestratorPlan) -> OrchestratorPlan:
        """Execute all tasks, respecting dependencies via phased execution.

        Runs independent tasks in parallel within each phase:
          Phase 1: Architect (no dependencies)
          Phase 2: Implementer (needs architect output)
          Phase 3: Tester (needs implementation)
          Phase 4: Reviewer (needs all prior outputs)
        """
        phases: list[list[SpecialistRole]] = [
            [SpecialistRole.ARCHITECT],
            [SpecialistRole.IMPLEMENTER],
            [SpecialistRole.TESTER],
            [SpecialistRole.REVIEWER],
        ]

        accumulated_context: dict[str, str] = {}

        for phase_roles in phases:
            tasks_in_phase = [
                t for t in plan.tasks if t.role in phase_roles
            ]
            if not tasks_in_phase:
                continue

            # Inject accumulated context from prior phases
            for task in tasks_in_phase:
                task.context.update(accumulated_context)

            # Run tasks in this phase in parallel
            results = await asyncio.gather(
                *[
                    self._specialists[t.role].execute(t)
                    for t in tasks_in_phase
                ],
                return_exceptions=True,
            )

            # Collect results for downstream phases
            for task, result in zip(tasks_in_phase, results):
                if isinstance(result, Exception):
                    task.mark_failed(str(result))
                else:
                    accumulated_context[task.role.value] = result

        return plan

    def synthesize(self, plan: OrchestratorPlan) -> str:
        """Synthesize specialist outputs into an integrated response."""
        outputs = "\n\n".join(
            f"=== {t.role.value.upper()} ===\n{t.result}"
            for t in plan.tasks
            if t.result
        )

        response = self.client.messages.create(
            model=self.config.orchestrator_model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": SYNTHESIS_PROMPT.format(
                        request=plan.original_request, outputs=outputs
                    ),
                }
            ],
        )
        plan.integrated_output = response.content[0].text
        return plan.integrated_output

    async def run(self, request: str) -> str:
        """Full pipeline: decompose → execute → synthesize."""
        print(f"[orchestrator] Decomposing request...")
        plan = self.decompose(request)
        print(f"[orchestrator] Created {len(plan.tasks)} tasks:")
        for t in plan.tasks:
            print(f"  - [{t.role.value}] {t.description[:80]}")

        print(f"\n[orchestrator] Executing tasks across specialists...")
        await self.execute_plan(plan)

        completed = sum(1 for t in plan.tasks if t.result)
        failed = sum(1 for t in plan.tasks if t.error)
        print(f"[orchestrator] Done: {completed} completed, {failed} failed")

        if plan.any_failed:
            failed_tasks = [t for t in plan.tasks if t.error]
            for t in failed_tasks:
                print(f"  [FAILED] [{t.role.value}] {t.error}")

        print(f"\n[orchestrator] Synthesizing integrated output...")
        return self.synthesize(plan)
