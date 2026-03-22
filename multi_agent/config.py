"""Configuration for the multi-agent system."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Runtime configuration."""

    api_key: str | None = None
    orchestrator_model: str = "claude-sonnet-4-20250514"
    specialist_model: str = "claude-haiku-4-5-20251001"
    max_parallel: int = 4
    max_retries: int = 2

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            orchestrator_model=os.environ.get(
                "AIO_ORCHESTRATOR_MODEL", cls.orchestrator_model
            ),
            specialist_model=os.environ.get(
                "AIO_SPECIALIST_MODEL", cls.specialist_model
            ),
            max_parallel=int(os.environ.get("AIO_MAX_PARALLEL", cls.max_parallel)),
        )
