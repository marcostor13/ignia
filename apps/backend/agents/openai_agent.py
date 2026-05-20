"""
OpenAIAgent: uses the OpenAI SDK with function-calling support.
"""

import json
import os
from typing import Any

from openai import AsyncOpenAI

from .base_agent import AgentConfig, BaseAgent
from ..token_efficiency.tracker import TokenTracker


class OpenAIAgent(BaseAgent):
    """Agent backed by OpenAI GPT with tool-calling support."""

    MODEL_ID = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

    def __init__(
        self,
        config: AgentConfig,
        tracker: TokenTracker,
        skill_registry: Any = None,
    ):
        super().__init__(config, tracker)
        self._client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
        self._skill_registry = skill_registry

    def _build_tools(self) -> list[dict]:
        if not self._skill_registry or not self.config.skills:
            return []
        tools = []
        for skill_name in self.config.skills:
            skill = self._skill_registry.get(skill_name)
            if skill:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": skill.name,
                        "description": skill.description,
                        "parameters": skill.parameters_schema,
                    },
                })
        return tools

    async def _handle_tool_call(self, tool_call: Any) -> str:
        if not self._skill_registry:
            return "Tool execution not available."
        tool_name = tool_call.function.name
        try:
            tool_input = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return "Invalid tool arguments."

        skill = self._skill_registry.get(tool_name)
        if not skill:
            return f"Unknown tool: {tool_name}"

        try:
            result = await skill.execute(**tool_input)
            return str(result.data) if result.success else f"Error: {result.data}"
        except Exception as exc:
            return f"Tool failed: {exc}"

    async def run(self, message: str, conversation_history: list[dict]) -> dict:
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")  # e.g. 2026-05-20
        system_with_date = (
            f"{self.config.system_prompt}\n\n"
            f"FECHA DE HOY: {today} (zona horaria Lima, UTC-5). "
            f"Usa esta fecha para resolver expresiones como 'mañana', 'hoy', 'el lunes', etc. "
            f"Convierte siempre a YYYY-MM-DD antes de llamar a schedule_meeting."
        )
        messages: list[dict] = [{"role": "system", "content": system_with_date}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        tools = self._build_tools()
        kwargs: dict[str, Any] = {
            "model": self.MODEL_ID,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response_text = ""
        total_input = 0
        total_output = 0
        action: str | None = None

        from ..skills.open_calendar import CALENDAR_TRIGGER

        try:
            resp = await self._client.chat.completions.create(**kwargs)
            total_input += resp.usage.prompt_tokens
            total_output += resp.usage.completion_tokens
            msg = resp.choices[0].message

            if msg.tool_calls:
                # Append assistant turn with tool_calls
                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
                })

                # Execute each tool and append results
                for tc in msg.tool_calls:
                    result = await self._handle_tool_call(tc)
                    if CALENDAR_TRIGGER in result:
                        action = "open_calendar"
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })

                # Final response after tools
                followup = await self._client.chat.completions.create(
                    model=self.MODEL_ID,
                    messages=messages,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )
                total_input += followup.usage.prompt_tokens
                total_output += followup.usage.completion_tokens
                response_text = followup.choices[0].message.content or ""
            else:
                response_text = msg.content or ""

        except Exception as exc:
            import traceback
            print(f"[OpenAIAgent] error: {type(exc).__name__}: {exc}")
            traceback.print_exc()
            response_text = "Lo siento, hubo un error técnico. Escríbenos a admin@ignia.site"

        record = self.tracker.record(
            agent_id=self.config.id,
            model=self.MODEL_ID,
            input_tokens=total_input,
            output_tokens=total_output,
            cached_tokens=0,
        )

        return {
            "response": response_text,
            "action": action,
            "tokens_used": {"input": total_input, "output": total_output, "cached": 0},
            "tokens_saved": record.tokens_saved,
            "cost_usd": record.cost_usd,
        }
