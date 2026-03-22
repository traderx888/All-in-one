"""Specialist D: Review and documentation agent."""

from ..models import SpecialistRole
from ..specialist import SpecialistAgent


class ReviewerAgent(SpecialistAgent):
    """Reviews code quality and produces documentation.

    Performs code review, checks for best practices, and generates
    user-facing and developer documentation.
    """

    role = SpecialistRole.REVIEWER
    system_prompt = (
        "You are an expert code reviewer and technical writer. Your role is to:\n"
        "- Review code for correctness, readability, and maintainability\n"
        "- Identify potential bugs, anti-patterns, and improvements\n"
        "- Write clear, concise documentation (README, API docs, usage guides)\n"
        "- Ensure consistency across the codebase\n"
        "- Provide actionable feedback with specific suggestions\n\n"
        "Output a structured review with findings and recommendations, "
        "plus any requested documentation."
    )
