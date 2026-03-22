"""Specialist C: Testing and validation agent."""

from ..models import SpecialistRole
from ..specialist import SpecialistAgent


class TesterAgent(SpecialistAgent):
    """Creates tests and validates implementation correctness.

    Writes test cases, identifies edge cases, and validates that the
    implementation meets the architectural specification.
    """

    role = SpecialistRole.TESTER
    system_prompt = (
        "You are an expert software tester and QA engineer. Your role is to:\n"
        "- Write comprehensive unit and integration tests\n"
        "- Identify edge cases and boundary conditions\n"
        "- Validate implementation against the design specification\n"
        "- Check for security vulnerabilities and error handling gaps\n"
        "- Suggest improvements based on testing findings\n\n"
        "Output test code and a validation report. Be thorough but "
        "pragmatic — focus on tests that catch real bugs."
    )
