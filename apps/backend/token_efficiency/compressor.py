"""
PromptCompressor: reduces token usage by removing filler words,
compressing conversation history, and extracting key sentences.
"""

import re
from typing import Any

# Words and phrases to strip from prompts to reduce noise
FILLER_PATTERNS = [
    # Politeness openers
    r"\bplease\b",
    r"\bcould you\b",
    r"\bwould you\b",
    r"\bcould you please\b",
    r"\bwould you please\b",
    r"\bi would like you to\b",
    r"\bi'd like you to\b",
    r"\bi want you to\b",
    r"\bcan you please\b",
    r"\bcan you\b",
    # Hedging
    r"\bkindly\b",
    r"\bjust\b(?!\s+\w+\s+enough)",  # "just" as filler, not "just enough"
    r"\bbasically\b",
    r"\bactually\b",
    r"\bliterally\b",
    r"\bsimply\b",
    r"\bessentially\b",
    r"\bfundamentally\b",
    r"\bobviously\b",
    r"\bclearly\b",
    # Verbose starters
    r"\bplease note that\b",
    r"\bit is important to note that\b",
    r"\bit should be noted that\b",
    r"\bplease be aware that\b",
    r"\bi would appreciate it if you could\b",
    r"\bi was wondering if you could\b",
    r"\bfeel free to\b",
    r"\bdon't hesitate to\b",
    # Ending fluff
    r"\bthanks in advance\b",
    r"\bthank you in advance\b",
    r"\bi appreciate your help\b",
    r"\bthank you for your help\b",
]

_FILLER_RE = re.compile(
    "|".join(FILLER_PATTERNS),
    flags=re.IGNORECASE,
)

_WHITESPACE_RE = re.compile(r"\s{2,}")
_SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")


class PromptCompressor:
    """Reduces token count while preserving semantic meaning."""

    def estimate_tokens(self, text: str) -> int:
        """Approximate token count using the len/4 heuristic."""
        return max(1, len(text) // 4)

    def remove_filler_words(self, text: str) -> str:
        """Remove polite filler words and hedging phrases."""
        compressed = _FILLER_RE.sub("", text)
        # Normalize whitespace created by removals
        compressed = _WHITESPACE_RE.sub(" ", compressed)
        # Fix sentence-initial lowercase introduced by prefix removal
        compressed = re.sub(
            r"(?<=[.!?]\s)([a-z])", lambda m: m.group(1).upper(), compressed
        )
        return compressed.strip()

    def extract_key_sentences(self, text: str, ratio: float = 0.7) -> str:
        """
        Keep the most important sentences by a simple heuristic:
        sentences with more unique content words are ranked higher.
        Always keeps the first and last sentence for context.
        """
        sentences = _SENTENCE_END_RE.split(text.strip())
        if len(sentences) <= 3:
            return text

        n_keep = max(2, int(len(sentences) * ratio))

        # Score by number of content words (words longer than 3 chars)
        def score(s: str) -> int:
            return sum(1 for w in s.split() if len(w) > 3)

        indexed = list(enumerate(sentences))
        # Always keep first and last
        must_keep = {0, len(sentences) - 1}
        optional = [(i, s) for i, s in indexed if i not in must_keep]

        # Sort optional by score descending, pick top n_keep - 2
        optional_sorted = sorted(optional, key=lambda x: score(x[1]), reverse=True)
        keep_indices = must_keep | {i for i, _ in optional_sorted[: n_keep - 2]}

        result = " ".join(s for i, s in indexed if i in keep_indices)
        return result

    def compress(self, text: str, ratio: float = 0.7) -> str:
        """
        Full compression pipeline:
        1. Remove filler words
        2. Extract key sentences based on ratio
        3. Normalize whitespace

        Args:
            text: Input text to compress.
            ratio: Fraction of sentences to keep (0.0–1.0). 1.0 = only filler removal.

        Returns:
            Compressed text.
        """
        text = self.remove_filler_words(text)
        if ratio < 1.0:
            text = self.extract_key_sentences(text, ratio=ratio)
        text = _WHITESPACE_RE.sub(" ", text).strip()
        return text

    def compress_conversation(
        self,
        messages: list[dict[str, Any]],
        max_tokens: int = 8000,
    ) -> list[dict[str, Any]]:
        """
        Trims a conversation to fit within max_tokens by removing oldest
        non-system messages first, preserving the system prompt if present.

        Args:
            messages: List of {"role": ..., "content": ...} dicts.
            max_tokens: Target maximum token budget.

        Returns:
            Trimmed messages list.
        """
        if not messages:
            return []

        # Separate system messages from conversation
        system_messages = [m for m in messages if m.get("role") == "system"]
        convo_messages = [m for m in messages if m.get("role") != "system"]

        system_tokens = sum(
            self.estimate_tokens(m.get("content", "")) for m in system_messages
        )
        budget = max_tokens - system_tokens

        # Work from newest messages backward, accumulating until budget is exceeded
        kept: list[dict] = []
        tokens_so_far = 0
        for msg in reversed(convo_messages):
            content = msg.get("content", "")
            t = self.estimate_tokens(content)
            if tokens_so_far + t > budget and kept:
                # Budget exceeded; stop adding older messages
                break
            kept.insert(0, msg)
            tokens_so_far += t

        return system_messages + kept
