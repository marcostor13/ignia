# Ignia — Agents Profile

For agentic pipelines and automation workflows.

**Verbosity:**
- Structured output only (JSON or YAML)
- No prose between tool calls
- Emit decisions, not reasoning

**Tool use:**
- Check if a skill exists before calling any API
- Always return SkillResult with success flag
- Prefer ContextCompressorSkill before long prompts

**Token budget:**
- Default max_tokens: 2048 for agents (not 4096)
- Use summarize skill when conversation > 10 turns
- Apply prompt caching on every system prompt >= 1024 tokens
