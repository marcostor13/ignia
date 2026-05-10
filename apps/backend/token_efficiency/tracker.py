from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# Pricing per 1M tokens (USD)
PRICING = {
    "claude-sonnet": {
        "input": 3.00,
        "output": 15.00,
        "cached": 0.30,
    },
    "claude-haiku": {
        "input": 0.25,
        "output": 1.25,
        "cached": 0.03,
    },
    "gemini-flash": {
        "input": 0.075,
        "output": 0.30,
        "cached": 0.01875,
    },
    "gemini-pro": {
        "input": 1.25,
        "output": 5.00,
        "cached": 0.3125,
    },
}

DEFAULT_PRICING = PRICING["claude-sonnet"]


def _resolve_pricing(model: str) -> dict:
    model_lower = model.lower()
    if model_lower == "demo":
        return {"input": 0.0, "output": 0.0, "cached": 0.0}
    if "haiku" in model_lower:
        return PRICING["claude-haiku"]
    if "sonnet" in model_lower or "claude" in model_lower:
        return PRICING["claude-sonnet"]
    if "flash" in model_lower:
        return PRICING["gemini-flash"]
    if "pro" in model_lower or "gemini" in model_lower:
        return PRICING["gemini-pro"]
    return DEFAULT_PRICING


def _calc_cost(input_tokens: int, output_tokens: int, cached_tokens: int, pricing: dict) -> float:
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    cached_cost = (cached_tokens / 1_000_000) * pricing["cached"]
    # Cached tokens replace input tokens in cost, so subtract the uncached rate
    # and add the cached rate for the cached portion
    input_non_cached = max(0, input_tokens - cached_tokens)
    actual_input_cost = (input_non_cached / 1_000_000) * pricing["input"]
    actual_cached_cost = (cached_tokens / 1_000_000) * pricing["cached"]
    total = actual_input_cost + actual_cached_cost + output_cost
    return round(total, 8)


def _calc_tokens_saved(cached_tokens: int, model: str) -> int:
    """Tokens saved is the number of cached tokens (not re-processed)."""
    return cached_tokens


@dataclass
class TokenUsageRecord:
    timestamp: datetime
    agent_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    tokens_saved: int
    cost_usd: float

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_tokens": self.cached_tokens,
            "tokens_saved": self.tokens_saved,
            "cost_usd": self.cost_usd,
        }


class TokenTracker:
    def __init__(self):
        self.records: list[TokenUsageRecord] = []

    def record(
        self,
        agent_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
    ) -> TokenUsageRecord:
        pricing = _resolve_pricing(model)
        tokens_saved = _calc_tokens_saved(cached_tokens, model)
        cost_usd = _calc_cost(input_tokens, output_tokens, cached_tokens, pricing)

        rec = TokenUsageRecord(
            timestamp=datetime.utcnow(),
            agent_id=agent_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            tokens_saved=tokens_saved,
            cost_usd=cost_usd,
        )
        self.records.append(rec)
        return rec

    def get_stats(self) -> dict:
        if not self.records:
            return {
                "total_records": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cached_tokens": 0,
                "total_tokens_saved": 0,
                "total_cost_usd": 0.0,
                "savings_percentage": 0.0,
                "by_model": {},
                "by_agent": {},
            }

        total_input = sum(r.input_tokens for r in self.records)
        total_output = sum(r.output_tokens for r in self.records)
        total_cached = sum(r.cached_tokens for r in self.records)
        total_saved = sum(r.tokens_saved for r in self.records)
        total_cost = round(sum(r.cost_usd for r in self.records), 6)

        savings_pct = round((total_saved / total_input * 100) if total_input > 0 else 0.0, 2)

        # Group by model
        by_model: dict[str, dict] = {}
        for r in self.records:
            m = r.model
            if m not in by_model:
                by_model[m] = {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cached_tokens": 0,
                    "cost_usd": 0.0,
                }
            by_model[m]["calls"] += 1
            by_model[m]["input_tokens"] += r.input_tokens
            by_model[m]["output_tokens"] += r.output_tokens
            by_model[m]["cached_tokens"] += r.cached_tokens
            by_model[m]["cost_usd"] = round(by_model[m]["cost_usd"] + r.cost_usd, 6)

        # Group by agent
        by_agent: dict[str, dict] = {}
        for r in self.records:
            a = r.agent_id
            if a not in by_agent:
                by_agent[a] = {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost_usd": 0.0,
                }
            by_agent[a]["calls"] += 1
            by_agent[a]["input_tokens"] += r.input_tokens
            by_agent[a]["output_tokens"] += r.output_tokens
            by_agent[a]["cost_usd"] = round(by_agent[a]["cost_usd"] + r.cost_usd, 6)

        return {
            "total_records": len(self.records),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cached_tokens": total_cached,
            "total_tokens_saved": total_saved,
            "total_cost_usd": total_cost,
            "savings_percentage": savings_pct,
            "by_model": by_model,
            "by_agent": by_agent,
        }

    def get_records(self, limit: int = 100) -> list[dict]:
        return [r.to_dict() for r in self.records[-limit:]]
