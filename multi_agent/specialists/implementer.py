"""Specialist B: Implementation and coding agent."""

from ..models import SpecialistRole
from ..specialist import SpecialistAgent


class ImplementerAgent(SpecialistAgent):
    """Writes production code based on architectural designs.

    Translates designs and specifications into working code, following
    best practices and the patterns established by the architect.
    """

    role = SpecialistRole.IMPLEMENTER
    system_prompt = (
        "You are an expert software engineer focused on implementation. "
        "Your role is to:\n"
        "- Write clean, production-ready code\n"
        "- Follow the architecture and design provided\n"
        "- Use appropriate language idioms and best practices\n"
        "- Handle edge cases and error conditions\n"
        "- Keep code simple, readable, and maintainable\n\n"
        "Output complete, working code. Include only necessary comments. "
        "Follow the file structure and interfaces specified in the design."
    )
