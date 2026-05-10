# Ignia — Coding Profile

Extends CLAUDE.md with coding-specific rules.

**Output:**
- Write the complete working file — no ellipsis, no "rest stays the same"
- Show only changed code when diff is smaller than full file
- Include imports

**Style:**
- Python: type hints, dataclasses, async/await, no global state
- TypeScript/Angular: standalone components, inject(), signals, no NgModules
- Prefer composition over inheritance

**Debugging:**
- Run the failing command and paste the exact error
- One hypothesis per response, not a list of five possibilities
