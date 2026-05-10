"""
ClaudeAgent: uses the Anthropic SDK with prompt caching enabled.

Prompt caching reduces input token costs by ~90% for repeated system prompts.
The system prompt is sent with cache_control={"type": "ephemeral"} so Anthropic
caches it server-side for up to 5 minutes (extendable on each request).
"""

import os
from typing import Any

import anthropic

from .base_agent import AgentConfig, BaseAgent
from ..token_efficiency.tracker import TokenTracker
from ..token_efficiency.prompt_cache import (
    CacheableSystemPrompt,
    build_cached_messages,
)
from ..token_efficiency.response_formatter import ResponseFormatter

_formatter = ResponseFormatter()


class ClaudeAgent(BaseAgent):
    """Agent backed by Anthropic Claude with prompt caching and tool_use support."""

    MODEL_ID = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

    def __init__(
        self,
        config: AgentConfig,
        tracker: TokenTracker,
        skill_registry: Any = None,
    ):
        super().__init__(config, tracker)
        self._client = anthropic.AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY", "")
        )
        self._skill_registry = skill_registry
        # Pre-build the cached system prompt block
        enriched_prompt = _formatter.format_system_prompt(
            config.system_prompt, profile="agents"
        )
        self._system_block = CacheableSystemPrompt(enriched_prompt).to_anthropic_block()

    def _build_tools(self) -> list[dict]:
        """Assemble tool definitions from the skill registry for this agent."""
        if not self._skill_registry or not self.config.skills:
            return []
        tools = []
        for skill_name in self.config.skills:
            skill = self._skill_registry.get(skill_name)
            if skill:
                tools.append(skill.to_tool_definition())
        return tools

    async def _handle_tool_use(self, tool_use_block: Any) -> str:
        """Execute a skill requested by the model and return the result as a string."""
        if not self._skill_registry:
            return "Tool execution not available."

        tool_name = tool_use_block.name
        tool_input = tool_use_block.input or {}

        skill = self._skill_registry.get(tool_name)
        if not skill:
            return f"Unknown tool: {tool_name}"

        try:
            result = await skill.execute(**tool_input)
            if result.success:
                return str(result.data)
            return f"Tool error: {result.data}"
        except Exception as exc:
            return f"Tool execution failed: {exc}"

    async def run(
        self,
        message: str,
        conversation_history: list[dict],
    ) -> dict:
        """
        Send a message to Claude and return the response with token metrics.

        Prompt caching is applied to:
          - The system prompt (always, if >= 1024 tokens)
          - The most recent user turn in multi-turn conversations
        """
        messages = build_cached_messages(conversation_history, cache_last_n_turns=1)
        messages.append({"role": "user", "content": message})

        tools = self._build_tools()
        create_kwargs: dict[str, Any] = {
            "model": self.MODEL_ID,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": self._system_block,
            "messages": messages,
        }
        if tools:
            create_kwargs["tools"] = tools

        response_text = ""
        total_input = 0
        total_output = 0
        total_cached = 0

        try:
            response = await self._client.messages.create(**create_kwargs)

            total_input = response.usage.input_tokens
            total_output = response.usage.output_tokens
            total_cached = getattr(response.usage, "cache_read_input_tokens", 0)

            # Handle tool_use blocks if present
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_result = await self._handle_tool_use(block)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_result,
                        }
                    )
                elif block.type == "text":
                    response_text += block.text

            # If tools were called, send results back for a final response
            if tool_results:
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

                followup = await self._client.messages.create(
                    model=self.MODEL_ID,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    system=self._system_block,
                    messages=messages,
                )
                total_input += followup.usage.input_tokens
                total_output += followup.usage.output_tokens
                total_cached += getattr(followup.usage, "cache_read_input_tokens", 0)

                for block in followup.content:
                    if hasattr(block, "text"):
                        response_text += block.text

        except anthropic.APIConnectionError as exc:
            response_text = f"Connection error: {exc}"
        except anthropic.AuthenticationError:
            response_text = "Authentication failed. Check ANTHROPIC_API_KEY."
        except anthropic.RateLimitError:
            response_text = "Rate limit exceeded. Please retry shortly."
        except anthropic.APIError as exc:
            response_text = f"Anthropic API error: {exc}"

        record = self.tracker.record(
            agent_id=self.config.id,
            model=self.MODEL_ID,
            input_tokens=total_input,
            output_tokens=total_output,
            cached_tokens=total_cached,
        )

        return {
            "response": response_text,
            "tokens_used": {
                "input": total_input,
                "output": total_output,
                "cached": total_cached,
            },
            "tokens_saved": record.tokens_saved,
            "cost_usd": record.cost_usd,
        }
