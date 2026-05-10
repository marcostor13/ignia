from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class SkillResult:
    success: bool
    data: Any
    tokens_used: int = 0


class BaseSkill(ABC):
    name: str
    description: str
    parameters_schema: dict  # JSON schema for tool_use input_schema

    @abstractmethod
    async def execute(self, **kwargs) -> SkillResult:
        pass

    def to_tool_definition(self) -> dict:
        """Return Anthropic-compatible tool definition."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters_schema,
        }
