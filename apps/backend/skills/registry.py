from .base_skill import BaseSkill
from .implementations import (
    WebSearchSkill,
    WriteCodeSkill,
    SummarizeSkill,
    TokenCalculatorSkill,
    ContextCompressorSkill,
)


class SkillRegistry:
    """Central registry for all available skills."""

    def __init__(self):
        self._skills: dict[str, BaseSkill] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        defaults: list[BaseSkill] = [
            WebSearchSkill(),
            WriteCodeSkill(),
            SummarizeSkill(),
            TokenCalculatorSkill(),
            ContextCompressorSkill(),
        ]
        for skill in defaults:
            self.register(skill)

    def register(self, skill: BaseSkill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> BaseSkill | None:
        return self._skills.get(name)

    def list_all(self) -> list[dict]:
        return [
            {
                "name": s.name,
                "description": s.description,
                "parameters_schema": s.parameters_schema,
            }
            for s in self._skills.values()
        ]

    def __contains__(self, name: str) -> bool:
        return name in self._skills
