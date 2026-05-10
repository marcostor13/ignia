"""
Utilities for Anthropic prompt caching and multi-turn caching strategies.

Anthropic requires a minimum of 1024 tokens in a cacheable block.
Cached tokens are billed at 10% of normal input cost.
"""

from typing import Any

MIN_TOKENS_FOR_CACHING = 1024  # Anthropic minimum cacheable block size


class CacheableSystemPrompt:
    """
    Wraps a system prompt string with cache_control metadata for Anthropic.

    Usage:
        csp = CacheableSystemPrompt("You are a helpful assistant...")
        system_block = csp.to_anthropic_block()
        # Pass system_block directly to client.messages.create(system=...)
    """

    def __init__(self, text: str, cache_type: str = "ephemeral"):
        self.text = text
        self.cache_type = cache_type

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def should_cache(self) -> bool:
        return self._estimate_tokens(self.text) >= MIN_TOKENS_FOR_CACHING

    def to_anthropic_block(self) -> list[dict[str, Any]]:
        """
        Returns the system prompt formatted as an Anthropic content block list.
        If the prompt is long enough, cache_control is added.
        """
        block: dict[str, Any] = {"type": "text", "text": self.text}
        if self.should_cache():
            block["cache_control"] = {"type": self.cache_type}
        return [block]

    def to_plain(self) -> str:
        return self.text


def build_cached_messages(
    conversation_history: list[dict[str, Any]],
    cache_last_n_turns: int = 1,
) -> list[dict[str, Any]]:
    """
    Builds an Anthropic-compatible message list with cache_control applied to
    the most recent user turn(s), enabling multi-turn prompt caching.

    Anthropic caches the prefix up to and including each cache_control breakpoint.
    Placing cache_control on recent user messages lets repeated similar requests
    reuse the cached conversation context.

    Args:
        conversation_history: List of {"role": ..., "content": ...} dicts.
        cache_last_n_turns: Number of most-recent user messages to mark for caching.

    Returns:
        A new list of messages with cache_control injected where appropriate.
    """
    if not conversation_history:
        return []

    messages = []
    user_indices = [
        i for i, m in enumerate(conversation_history) if m.get("role") == "user"
    ]
    cache_indices = set(user_indices[-cache_last_n_turns:]) if user_indices else set()

    for i, msg in enumerate(conversation_history):
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if i in cache_indices and isinstance(content, str):
            token_estimate = max(1, len(content) // 4)
            if token_estimate >= MIN_TOKENS_FOR_CACHING:
                messages.append(
                    {
                        "role": role,
                        "content": [
                            {
                                "type": "text",
                                "text": content,
                                "cache_control": {"type": "ephemeral"},
                            }
                        ],
                    }
                )
            else:
                messages.append({"role": role, "content": content})
        else:
            messages.append({"role": role, "content": content})

    return messages


def add_cache_to_large_system_prompt(system_prompt: str) -> list[dict[str, Any]] | str:
    """
    Convenience helper. Returns a cached block list if the prompt is large enough,
    otherwise returns the plain string (Anthropic accepts both formats).
    """
    csp = CacheableSystemPrompt(system_prompt)
    if csp.should_cache():
        return csp.to_anthropic_block()
    return system_prompt
