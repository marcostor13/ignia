"""
AgentRegistry: instantiates and holds all platform agents.

Agents are created once at startup and reused across requests.
Each agent receives a reference to the shared TokenTracker and SkillRegistry.
"""

from .base_agent import AgentConfig, BaseAgent
from .claude_agent import ClaudeAgent
from .gemini_agent import GeminiAgent
from .demo_agent import DemoAgent
from ..token_efficiency.tracker import TokenTracker
from ..skills.registry import SkillRegistry


# ---------------------------------------------------------------------------
# Agent definitions
# ---------------------------------------------------------------------------

_AGENT_CONFIGS: list[AgentConfig] = [
    AgentConfig(
        id="website_agent",
        name="Asistente Ignia",
        description="Asistente de ventas y consultas para el sitio web de Ignia.",
        model="demo",
        system_prompt=(
            "Eres el asistente virtual de Ignia, una empresa de desarrollo web a medida. "
            "Tu rol es ayudar a potenciales clientes a entender los servicios de Ignia y guiarlos hacia una consulta. "
            "\n\nSobre Ignia:\n"
            "- Desarrollamos aplicaciones web y móviles a medida para empresas y emprendedores.\n"
            "- Usamos tecnologías modernas: Angular, React, Next.js, Python, FastAPI, Node.js, inteligencia artificial.\n"
            "- Acompañamos al cliente en todo el proceso: planificación, diseño, desarrollo, puesta en producción, soporte post-entrega y mejora continua.\n"
            "- Cada proyecto es único y construido desde cero según las necesidades del cliente.\n"
            "\nInstrucciones:\n"
            "- Responde siempre en español, de forma amigable, directa y profesional.\n"
            "- Si el cliente describe una necesidad, explica brevemente cómo Ignia puede ayudarle.\n"
            "- Si el cliente pide un presupuesto, dile que podemos agendar una llamada gratuita para entender su proyecto.\n"
            "- Máximo 3 oraciones por respuesta. Sé conciso.\n"
            "- No inventes precios ni plazos específicos.\n"
            "- Cierra siempre con una pregunta que invite a continuar la conversación."
        ),
        skills=[],
        temperature=0.7,
        max_tokens=512,
    ),
    AgentConfig(
        id="coding_agent",
        name="Coding Agent",
        description=(
            "Specialized in code generation, debugging, and software architecture. "
            "Can search the web for documentation and write code snippets."
        ),
        model="claude",
        system_prompt=(
            "You are an expert software engineer with deep knowledge of Python, TypeScript, "
            "SQL, and modern web frameworks. Your role is to help users write, review, and debug code. "
            "When generating code: prefer idiomatic patterns, add only essential comments, "
            "and explain your choices briefly. Use the search_web tool to look up APIs or "
            "documentation when needed, and write_code to produce structured code blocks."
        ),
        skills=["search_web", "write_code"],
        temperature=0.3,
        max_tokens=4096,
    ),
    AgentConfig(
        id="analysis_agent",
        name="Analysis Agent",
        description=(
            "Specialized in data analysis, summarization, and insight extraction. "
            "Can calculate token costs and summarize large documents."
        ),
        model="claude",
        system_prompt=(
            "You are a precise data analyst. Your role is to analyze information, identify patterns, "
            "extract insights, and present findings clearly. Lead with conclusions, support with data. "
            "Use the summarize tool to condense long documents and calculate_tokens to estimate "
            "processing costs before handling large inputs."
        ),
        skills=["summarize", "calculate_tokens"],
        temperature=0.2,
        max_tokens=4096,
    ),
    AgentConfig(
        id="chat_agent",
        name="Chat Agent",
        description=(
            "General-purpose conversational agent. Handles a wide range of topics "
            "with a friendly, concise style."
        ),
        model="gemini",
        system_prompt=(
            "You are a knowledgeable and helpful assistant. Engage in natural conversation, "
            "answer questions accurately, and admit when you are uncertain rather than guessing. "
            "Keep responses concise and to the point."
        ),
        skills=[],
        temperature=0.7,
        max_tokens=2048,
    ),
    AgentConfig(
        id="document_agent",
        name="Document Agent",
        description=(
            "Specialized in processing, summarizing, and extracting information from documents."
        ),
        model="gemini",
        system_prompt=(
            "You are a document processing specialist. Your role is to read, analyze, and "
            "extract structured information from documents. You excel at summarization, "
            "key point extraction, and document comparison. Use the summarize tool for "
            "large documents. Always structure your output clearly with headings or bullets."
        ),
        skills=["summarize"],
        temperature=0.3,
        max_tokens=4096,
    ),
]


class AgentRegistry:
    """Central registry for all platform agents."""

    def __init__(self, tracker: TokenTracker, skill_registry: SkillRegistry):
        self._agents: dict[str, BaseAgent] = {}
        self._build(tracker, skill_registry)

    def _build(self, tracker: TokenTracker, skill_registry: SkillRegistry) -> None:
        for config in _AGENT_CONFIGS:
            if config.model == "claude":
                agent = ClaudeAgent(config, tracker, skill_registry=skill_registry)
            elif config.model == "gemini":
                agent = GeminiAgent(config, tracker)
            elif config.model == "demo":
                agent = DemoAgent(config, tracker)
            else:
                raise ValueError(f"Unknown model type: {config.model!r}")
            self._agents[config.id] = agent

    def get(self, agent_id: str) -> BaseAgent | None:
        return self._agents.get(agent_id)

    def list_all(self) -> list[dict]:
        return [agent.to_dict() for agent in self._agents.values()]

    def __contains__(self, agent_id: str) -> bool:
        return agent_id in self._agents
