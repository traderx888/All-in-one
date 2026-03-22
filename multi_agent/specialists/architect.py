"""Specialist A: Architecture and design agent."""

from ..models import SpecialistRole
from ..specialist import SpecialistAgent


class ArchitectAgent(SpecialistAgent):
    """Designs system architecture, data models, and API contracts.

    Focuses on high-level structure, component boundaries, and technical
    decision-making before implementation begins.
    """

    role = SpecialistRole.ARCHITECT
    system_prompt = (
        "You are an expert software architect. Your role is to:\n"
        "- Design clean, scalable system architectures\n"
        "- Define component boundaries and interfaces\n"
        "- Choose appropriate design patterns and data models\n"
        "- Identify potential technical risks and trade-offs\n"
        "- Produce clear architectural documents and diagrams (in text)\n\n"
        "Output structured designs that an implementation team can follow. "
        "Be specific about file structure, module responsibilities, and "
        "data flow between components."
    )
