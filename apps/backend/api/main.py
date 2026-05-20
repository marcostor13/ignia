"""
Ignia AI Agents Platform — FastAPI backend.

Routes:
  POST /api/chat              - Chat with an agent
  GET  /api/agents            - List all agents
  GET  /api/skills            - List all skills
  POST /api/agents/{id}/run   - Run a specific agent (alias for chat)
  GET  /api/token-stats       - Token usage statistics
  POST /api/compress          - Compress a prompt
"""

import os
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# IP rate limiter — 20 requests per IP per hour
# ---------------------------------------------------------------------------

_CHAT_LIMIT = int(os.environ.get("CHAT_RATE_LIMIT", "20"))
_CHAT_WINDOW = 3600  # seconds

_ip_log: dict[str, list[float]] = defaultdict(list)


def _allow_request(ip: str) -> bool:
    now = time.time()
    cutoff = now - _CHAT_WINDOW
    hits = _ip_log[ip]
    # drop timestamps outside the window
    _ip_log[ip] = [t for t in hits if t > cutoff]
    if len(_ip_log[ip]) >= _CHAT_LIMIT:
        return False
    _ip_log[ip].append(now)
    return True

load_dotenv()

# ---------------------------------------------------------------------------
# Shared state — instantiated once at startup
# ---------------------------------------------------------------------------

from ..token_efficiency.tracker import TokenTracker
from ..skills.registry import SkillRegistry
from ..agents.registry import AgentRegistry
from ..token_efficiency.compressor import PromptCompressor
from .leads import router as leads_router

_tracker = TokenTracker()
_skill_registry = SkillRegistry()
_agent_registry = AgentRegistry(tracker=_tracker, skill_registry=_skill_registry)
_compressor = PromptCompressor()


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Ignia backend starting up.")
    print(f"  Agents loaded: {[a['id'] for a in _agent_registry.list_all()]}")
    print(f"  Skills loaded: {[s['name'] for s in _skill_registry.list_all()]}")
    yield
    # Shutdown
    print("Ignia backend shutting down.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Ignia AI Agents Platform",
    description="Backend API for multi-agent AI platform with token efficiency.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(leads_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    agent_id: str = Field(default="chat_agent", description="Agent to use")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for history")
    model: Optional[str] = Field(default=None, description="Override model: 'claude' or 'gemini'")
    conversation_history: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Prior conversation turns [{'role': ..., 'content': ...}]",
    )


class ChatResponse(BaseModel):
    response: str
    agent_id: str
    tokens_used: dict[str, int]
    tokens_saved: int
    cost_usd: float
    action: Optional[str] = None  # "open_calendar" → frontend opens booking modal


class AgentRunRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_history: list[dict[str, Any]] = Field(default_factory=list)


class CompressRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to compress")
    ratio: float = Field(default=0.7, ge=0.1, le=1.0, description="Compression ratio")


class CompressResponse(BaseModel):
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    tokens_saved: int
    savings_percentage: float


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
async def chat(http_request: Request, request: ChatRequest) -> ChatResponse:
    """Chat with an agent. Supports multi-turn conversation history."""
    ip = http_request.client.host if http_request.client else "unknown"
    if not _allow_request(ip):
        raise HTTPException(
            status_code=429,
            detail="Demasiadas solicitudes. Por favor espera unos minutos antes de continuar.",
        )

    agent = _agent_registry.get(request.agent_id)
    if agent is None:
        available = [a["id"] for a in _agent_registry.list_all()]
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{request.agent_id}' not found. Available: {available}",
        )

    result = await agent.run(
        message=request.message,
        conversation_history=request.conversation_history,
    )

    return ChatResponse(
        response=result["response"],
        agent_id=request.agent_id,
        tokens_used=result.get("tokens_used", {}),
        tokens_saved=result.get("tokens_saved", 0),
        cost_usd=result.get("cost_usd", 0.0),
        action=result.get("action"),
    )


@app.get("/api/agents")
async def list_agents() -> dict:
    """Return all registered agents."""
    return {"agents": _agent_registry.list_all()}


@app.get("/api/skills")
async def list_skills() -> dict:
    """Return all registered skills with their parameter schemas."""
    return {"skills": _skill_registry.list_all()}


@app.post("/api/agents/{agent_id}/run", response_model=ChatResponse)
async def run_agent(agent_id: str, request: AgentRunRequest) -> ChatResponse:
    """Run a specific agent directly by ID."""
    agent = _agent_registry.get(agent_id)
    if agent is None:
        available = [a["id"] for a in _agent_registry.list_all()]
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_id}' not found. Available: {available}",
        )

    result = await agent.run(
        message=request.message,
        conversation_history=request.conversation_history,
    )

    return ChatResponse(
        response=result["response"],
        agent_id=agent_id,
        tokens_used=result.get("tokens_used", {}),
        tokens_saved=result.get("tokens_saved", 0),
        cost_usd=result.get("cost_usd", 0.0),
        action=result.get("action"),
    )


@app.get("/api/token-stats")
async def get_token_stats() -> dict:
    """Return aggregated token usage statistics and recent records."""
    stats = _tracker.get_stats()
    recent = _tracker.get_records(limit=50)
    return {"stats": stats, "recent_records": recent}


@app.post("/api/compress", response_model=CompressResponse)
async def compress_prompt(request: CompressRequest) -> CompressResponse:
    """Compress a prompt to reduce token usage."""
    original_tokens = _compressor.estimate_tokens(request.text)
    compressed = _compressor.compress(request.text, ratio=request.ratio)
    compressed_tokens = _compressor.estimate_tokens(compressed)
    saved = original_tokens - compressed_tokens
    savings_pct = round((saved / original_tokens * 100) if original_tokens > 0 else 0.0, 1)

    return CompressResponse(
        compressed_text=compressed,
        original_tokens=original_tokens,
        compressed_tokens=compressed_tokens,
        tokens_saved=saved,
        savings_percentage=savings_pct,
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "agents": len(_agent_registry.list_all())}
