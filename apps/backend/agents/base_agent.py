from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..token_efficiency.tracker import TokenTracker


@dataclass
class AgentConfig:
    id: str
    name: str
    description: str
    model: str  # "claude" or "gemini"
    system_prompt: str
    skills: list[str] = field(default_factory=list)
    temperature: float = 0.7
    max_tokens: int = 4096


class BaseAgent(ABC):
    def __init__(self, config: AgentConfig, tracker: TokenTracker):
        self.config = config
        self.tracker = tracker

    @abstractmethod
    async def run(self, message: str, conversation_history: list[dict]) -> dict:
        """
        Execute the agent with the given user message and conversation history.

        Args:
            message: The user's latest message.
            conversation_history: Prior turns as list of {"role": ..., "content": ...}.

        Returns:
            dict with at minimum:
                - "response": str
                - "tokens_used": dict
                - "tokens_saved": int
        """
        pass

    def to_dict(self) -> dict:
        return {
            "id": self.config.id,
            "name": self.config.name,
            "description": self.config.description,
            "model": self.config.model,
            "skills": self.config.skills,
        }
