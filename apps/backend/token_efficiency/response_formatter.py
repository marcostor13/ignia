"""
ResponseFormatter: injects terse response rules into system prompts to reduce
output token usage without sacrificing quality.
"""

from typing import Literal

Profile = Literal["default", "coding", "agents", "analysis"]

# Core terse rules - inspired by token-efficient prompting best practices
_TERSE_BASE = """
RESPONSE RULES (follow strictly):
- Answer directly. Never restate the question or summarize what you are about to do.
- No pleasantries, greetings, or sign-offs (no "Great!", "Sure!", "Of course!", "Certainly!").
- No filler phrases ("As an AI...", "I'd be happy to...", "That's a great question").
- Use the minimum words needed. Prefer bullet points over paragraphs when listing items.
- Code: provide only the requested code plus essential inline comments. No boilerplate preamble.
- Omit caveats unless they are critical to correctness.
""".strip()

_PROFILES: dict[Profile, str] = {
    "default": _TERSE_BASE,
    "coding": _TERSE_BASE
    + """
- Output code blocks immediately. Explain after, briefly, only if non-obvious.
- Use standard idiomatic patterns. Do not explain language basics.
- If asked to fix a bug: show only the corrected code and a one-line explanation.
""".strip(),
    "agents": _TERSE_BASE
    + """
- When reporting tool/skill results: one line per result, no narrative.
- Report errors as: ERROR: <message>. Do not apologize.
- Status updates: present tense, imperative mood ("Searching...", "Done.").
""".strip(),
    "analysis": _TERSE_BASE
    + """
- Lead with the conclusion, then supporting data.
- Numbers: include units and precision appropriate to the domain.
- Omit methodology unless asked.
""".strip(),
}


class ResponseFormatter:
    """Manages terse response profiles and system prompt augmentation."""

    def get_terse_system_addon(self, profile: Profile = "default") -> str:
        """
        Returns the terse response ruleset for the given profile.

        Args:
            profile: One of "default", "coding", "agents", "analysis".

        Returns:
            Formatted string to append to a system prompt.
        """
        rules = _PROFILES.get(profile, _PROFILES["default"])
        return f"\n\n---\n{rules}"

    def format_system_prompt(
        self,
        base_prompt: str,
        profile: Profile = "default",
    ) -> str:
        """
        Appends the appropriate terse rules to a base system prompt.

        Args:
            base_prompt: The agent's core system prompt.
            profile: Verbosity/style profile.

        Returns:
            Combined system prompt with terse rules appended.
        """
        addon = self.get_terse_system_addon(profile)
        return base_prompt.rstrip() + addon

    def get_available_profiles(self) -> list[str]:
        return list(_PROFILES.keys())
