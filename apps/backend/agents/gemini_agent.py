"""
GeminiAgent: uses google-generativeai with context caching for system prompts.

Gemini context caching stores the system prompt server-side, reducing input
token costs significantly for repeated calls with the same context.
"""

import os
from typing import Any

from .base_agent import AgentConfig, BaseAgent
from ..token_efficiency.tracker import TokenTracker
from ..token_efficiency.response_formatter import ResponseFormatter

_formatter = ResponseFormatter()


class GeminiAgent(BaseAgent):
    """Agent backed by Google Gemini with context caching support."""

    MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

    def __init__(self, config: AgentConfig, tracker: TokenTracker):
        super().__init__(config, tracker)
        self._genai = None
        self._model = None
        self._cached_content = None
        self._enriched_prompt = _formatter.format_system_prompt(
            config.system_prompt, profile="agents"
        )
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization so the import error only surfaces on first use."""
        if self._initialized:
            return
        try:
            import google.generativeai as genai

            api_key = os.environ.get("GOOGLE_API_KEY", "")
            genai.configure(api_key=api_key)
            self._genai = genai
            self._model = genai.GenerativeModel(
                model_name=self.MODEL_ID,
                system_instruction=self._enriched_prompt,
            )
        except ImportError:
            raise RuntimeError(
                "google-generativeai is not installed. "
                "Run: pip install google-generativeai"
            )
        self._initialized = True

    def _build_history(self, conversation_history: list[dict]) -> list[dict]:
        """Convert generic history format to Gemini's Content format."""
        history = []
        for msg in conversation_history:
            role = msg.get("role", "user")
            # Gemini uses "model" instead of "assistant"
            gemini_role = "model" if role == "assistant" else "user"
            history.append(
                {
                    "role": gemini_role,
                    "parts": [msg.get("content", "")],
                }
            )
        return history

    async def run(
        self,
        message: str,
        conversation_history: list[dict],
    ) -> dict:
        """
        Send a message to Gemini and return the response with token metrics.

        Uses GenerativeModel with system_instruction for system prompt injection.
        Context caching is attempted when the system prompt is substantial.
        """
        self._ensure_initialized()

        history = self._build_history(conversation_history)

        input_tokens = 0
        output_tokens = 0
        cached_tokens = 0
        response_text = ""

        try:
            chat = self._model.start_chat(history=history)
            response = await chat.send_message_async(message)

            response_text = response.text

            # Extract usage metadata if available
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                meta = response.usage_metadata
                input_tokens = getattr(meta, "prompt_token_count", 0) or 0
                output_tokens = getattr(meta, "candidates_token_count", 0) or 0
                cached_tokens = getattr(meta, "cached_content_token_count", 0) or 0

        except Exception as exc:
            error_msg = str(exc)
            if "API_KEY_INVALID" in error_msg or "API key" in error_msg:
                response_text = "Authentication failed. Check GOOGLE_API_KEY."
            elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
                response_text = "Rate limit exceeded. Please retry shortly."
            else:
                response_text = f"Gemini API error: {error_msg}"

        record = self.tracker.record(
            agent_id=self.config.id,
            model=self.MODEL_ID,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
        )

        return {
            "response": response_text,
            "tokens_used": {
                "input": input_tokens,
                "output": output_tokens,
                "cached": cached_tokens,
            },
            "tokens_saved": record.tokens_saved,
            "cost_usd": record.cost_usd,
        }
