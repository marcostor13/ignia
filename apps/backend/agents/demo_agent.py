"""
DemoAgent: smart keyword-based responder for the Ignia website chat.
Uses scored multi-keyword matching and conversation context. No API key needed.
"""

import random
from .base_agent import AgentConfig, BaseAgent
from ..token_efficiency.tracker import TokenTracker


# Each entry: (keywords_list, weight, replies_list)
# Weight = how strongly this category matches each keyword hit.
# The category with the highest total score wins.
_CATEGORIES: list[tuple[list[str], list[str]]] = [
    # --- Saludos ---
    (
        ["hola", "buenas", "buenos días", "buen día", "buenas tardes", "buenas noches",
         "hello", "hi", "hey", "saludos", "bienvenido"],
        [
            "¡Hola! Soy el asistente de Ignia. Nos especializamos en desarrollar aplicaciones web a medida. ¿Tienes algún proyecto en mente?",
            "¡Buenas! Bienvenido a Ignia. Construimos plataformas web y aplicaciones a medida para empresas y emprendedores. ¿En qué te puedo ayudar?",
        ],
    ),
    # --- Precio / Presupuesto ---
    (
        ["precio", "costo", "cuánto", "cuanto", "presupuesto", "cobran", "tarifa",
         "inversión", "inversion", "vale", "valor", "pagan", "pago", "económico",
         "barato", "caro", "cotización", "cotizacion", "quote"],
        [
            "Cada proyecto es único, por eso no manejamos tarifas fijas. Agendamos una llamada gratuita de 30 minutos para entender tu proyecto y darte una propuesta real. ¿Me cuentas qué quieres construir?",
            "El costo depende del alcance, tecnologías y plazos. Después de una llamada de 30 minutos sin compromiso podemos darte un número concreto. ¿Cuál es tu idea?",
        ],
    ),
    # --- Tiempo / Plazos ---
    (
        ["cuanto tiempo", "cuánto tiempo", "tarda", "tardan", "tiempo", "cuánto tarda",
         "cuanto tarda", "plazo", "demora", "cuando estaria", "rápido", "rapido",
         "urgente", "semanas", "meses", "fecha", "entrega"],
        [
            "Los plazos dependen del alcance: una landing page toma 2-3 semanas, una plataforma compleja entre 2 y 4 meses. Trabajamos en sprints para que veas avances semanales. ¿Tienes algún plazo específico?",
            "Depende del proyecto. Trabajamos por etapas para que puedas ver resultados reales semana a semana, no solo al final. ¿Hay alguna fecha límite que debamos respetar?",
        ],
    ),
    # --- Tecnología ---
    (
        ["tecnología", "tecnologias", "angular", "react", "next", "python", "fastapi",
         "node", "stack", "lenguaje", "framework", "base de datos", "database",
         "postgresql", "mongodb", "firebase", "aws", "cloud", "hosting"],
        [
            "Usamos Angular, React y Next.js para el frontend; Python con FastAPI y Node.js para el backend; PostgreSQL o MongoDB para datos. El stack lo elegimos según lo que mejor sirve a tu proyecto. ¿Tienes alguna preferencia?",
            "Seleccionamos el stack técnico según las necesidades reales: Angular para apps complejas, Next.js para sitios rápidos, Python para backends robustos e IA integrada. ¿Qué necesita tu proyecto?",
        ],
    ),
    # --- IA / Automatización ---
    (
        ["ia", "inteligencia artificial", "chatbot", "ai", "machine learning",
         "automatizar", "automatización", "bot", "gpt", "claude", "gemini",
         "recomendaciones", "predicción", "prediccion"],
        [
            "Integramos IA cuando agrega valor real: chatbots de atención, análisis de datos, recomendaciones personalizadas, automatización de procesos. ¿Qué parte de tu negocio quieres potenciar con IA?",
            "Trabajamos con modelos de Claude, Gemini y GPT según el caso de uso. La IA es una herramienta, no un fin en sí mismo. ¿Qué problema concreto quieres resolver?",
        ],
    ),
    # --- E-commerce / Tienda ---
    (
        ["ecommerce", "e-commerce", "tienda", "venta online", "shop", "carrito",
         "productos", "catálogo", "catalogo", "pago", "stripe", "mercadopago",
         "woocommerce", "shopify", "ventas"],
        [
            "Desarrollamos e-commerce a medida: catálogos dinámicos, pagos integrados (Stripe, MercadoPago), panel de administración propio y optimización de conversión. ¿Ya tienes productos o partes desde cero?",
            "Una tienda online bien construida supera a plataformas genéricas en rendimiento y conversión. La hacemos sobre Angular o Next.js con backend Python. ¿Cuántos productos manejarías?",
        ],
    ),
    # --- Restaurante / Pedidos / Delivery / Gastronomía ---
    (
        ["restaurante", "restaurantes", "restaurant", "pedido", "pedidos", "delivery",
         "domicilio", "comida", "gastronomía", "gastronomia", "menu", "menú", "mesa",
         "reserva", "reservas", "carta", "plato", "cocina", "food", "orden", "ordenes",
         "bar", "cafetería", "cafeteria", "take away", "takeaway", "online ordering",
         "para llevar", "cocinas"],
        [
            "¡Perfecto! Construimos plataformas para restaurantes: gestión de pedidos online, delivery con tracking, administración de menú en tiempo real y panel de reportes. ¿Necesitas también sistema de reservas o solo pedidos y delivery?",
            "Tenemos experiencia en plataformas gastronómicas: pedidos online, delivery con seguimiento GPS, integración con impresoras de cocina y pagos digitales. ¿Cuántos locales manejarías? ¿Es una cadena o un solo restaurante?",
            "Una plataforma de pedidos para restaurantes puede incluir: app web para el cliente, panel de cocina en tiempo real, gestión de delivery y reportes de ventas. ¿Qué funcionalidades son prioritarias para ti?",
        ],
    ),
    # --- SaaS / Plataforma / Sistema ---
    (
        ["plataforma", "sistema", "saas", "software", "aplicación", "aplicacion",
         "app", "web app", "dashboard", "panel", "gestión", "gestion", "erp",
         "crm", "administración", "administracion", "módulo", "modulo"],
        [
            "Desarrollamos plataformas web y SaaS a medida: desde sistemas de gestión internos hasta productos que escalan a miles de usuarios. ¿Cuál es el problema principal que quieres resolver con la plataforma?",
            "Construimos aplicaciones web complejas con Angular o React en el frontend y Python/Node en el backend. ¿Es para uso interno de tu empresa o es un producto para clientes finales?",
        ],
    ),
    # --- Mobile / App ---
    (
        ["móvil", "movil", "moviles", "móviles", "mobile", "iphone", "android", "ios",
         "aplicación móvil", "app móvil", "apps moviles", "apps móviles", "app nativa",
         "pwa", "celular", "smartphone", "nativa", "react native", "flutter"],
        [
            "Desarrollamos apps móviles con React Native o PWA (Progressive Web App) que funcionan en iOS y Android. ¿Necesitas una app nativa o una web app que funcione como app en el celular?",
            "Para móvil tenemos dos enfoques: PWA (más económico, mismo código que la web) o React Native (experiencia nativa). La elección depende del presupuesto y los requisitos. ¿Cuál es tu caso?",
        ],
    ),
    # --- Proceso / Metodología ---
    (
        ["proceso", "cómo trabajan", "como trabajan", "metodología", "metodologia",
         "etapas", "pasos", "agile", "scrum", "sprint", "cómo funciona", "como funciona"],
        [
            "Trabajamos en 5 etapas: 1) Planificación, 2) Diseño y prototipo, 3) Desarrollo iterativo por sprints, 4) Testing y deploy, 5) Acompañamiento post-lanzamiento. Cada sprint dura 2 semanas y tiene entregables claros. ¿Quieres saber más de alguna etapa?",
            "Usamos metodología ágil: sprints de 2 semanas, demos reales al final de cada sprint, comunicación directa sin intermediarios. Nada entra a desarrollo sin estar bien definido primero. ¿Prefieres estar muy involucrado o que te informemos solo en los hitos?",
        ],
    ),
    # --- Soporte / Post-entrega ---
    (
        ["soporte", "mantenimiento", "post-entrega", "después", "despues", "continua",
         "mejora", "actualización", "actualizacion", "bug", "error", "fix", "ayuda"],
        [
            "No desaparecemos al entregar. Ofrecemos soporte post-lanzamiento: corrección de bugs, actualizaciones, monitoreo de performance y mejora continua basada en datos reales. ¿Qué nivel de acompañamiento necesitas?",
            "El post-entrega es parte de nuestro proceso estándar: monitoreo, analytics, iteraciones y soporte técnico. ¿Tienes equipo técnico propio o necesitas que gestionemos todo?",
        ],
    ),
    # --- Contacto ---
    (
        ["contacto", "hablar", "reunión", "reunion", "llamada", "email", "correo",
         "whatsapp", "agendar", "cita", "demo", "información", "informacion", "más info"],
        [
            "Podemos agendar una llamada gratuita de 30 minutos sin compromiso. Escríbenos a hola@ignia.dev y te confirmamos horario ese mismo día. ¿Cuándo tienes disponibilidad?",
            "La mejor forma de empezar es una llamada corta: en 30 minutos entendemos tu proyecto y te damos una dirección clara. Escríbenos a hola@ignia.dev. ¿Te viene bien esta semana?",
        ],
    ),
    # --- Portfolio / Proyectos ---
    (
        ["portfolio", "proyectos", "trabajos", "ejemplos", "referencias", "clientes",
         "experiencia", "casos", "hicieron", "hizo", "trabajo anterior"],
        [
            "Hemos construido e-commerce especializados, dashboards de analytics, plataformas de gestión y aplicaciones con IA integrada. Puedes ver algunos proyectos en la sección de esta página. ¿Hay algún tipo de proyecto que te interese más?",
            "Tenemos experiencia en retail, gastronomía, SaaS, herramientas internas y marketing digital. ¿Cuál de esos sectores se parece más a tu proyecto?",
        ],
    ),
    # --- Agradecimiento / Confirmación ---
    (
        ["gracias", "ok", "genial", "perfecto", "excelente", "bien", "entendido",
         "claro", "de acuerdo", "chevere", "chévere", "dale", "buenísimo"],
        [
            "Con gusto. ¿Hay algo más que quieras saber sobre cómo Ignia puede ayudar a tu proyecto?",
            "¡Perfecto! Si quieres avanzar, el próximo paso es una llamada de 30 minutos para definir el alcance. ¿Te interesa agendarla?",
        ],
    ),
]

_DEFAULT_RESPONSES = [
    "Interesante. Para orientarte mejor, ¿puedes contarme más sobre el objetivo principal de tu proyecto?",
    "Cuéntame más sobre tu idea. ¿Es para uso interno de tu empresa o es un producto para clientes finales?",
    "En Ignia acompañamos todo el proceso: planificación, desarrollo, lanzamiento y mejora continua. ¿Por qué parte te gustaría empezar?",
    "¿Tienes ya alguna referencia de plataforma similar a lo que buscas? Eso nos ayuda mucho a entender la visión.",
]


def _score(text: str, keywords: list[str]) -> int:
    """Count keyword hits using whole-word / whole-phrase matching."""
    padded = f" {text} "  # pad so " kw " works at start/end of string
    return sum(1 for kw in keywords if f" {kw} " in padded or f" {kw}," in padded
               or f" {kw}." in padded or f" {kw}?" in padded or f" {kw}!" in padded)


class DemoAgent(BaseAgent):
    """Keyword-scored smart responder. No API key required."""

    def __init__(self, config: AgentConfig, tracker: TokenTracker):
        super().__init__(config, tracker)

    def _pick_response(self, message: str, history: list[dict]) -> str:
        current = message.lower()

        # Score ONLY on the current message — history must not override user's intent
        best_score = 0
        best_replies: list[str] = []

        for keywords, replies in _CATEGORIES:
            score = _score(current, keywords)
            if score > best_score:
                best_score = score
                best_replies = replies

        if best_score == 0 or not best_replies:
            return random.choice(_DEFAULT_RESPONSES)

        return random.choice(best_replies)

    async def run(self, message: str, conversation_history: list[dict]) -> dict:
        response = self._pick_response(message, conversation_history)

        input_tokens = max(1, len(message) // 4)
        output_tokens = max(1, len(response) // 4)

        record = self.tracker.record(
            agent_id=self.config.id,
            model="demo",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=0,
        )

        return {
            "response": response,
            "tokens_used": {"input": input_tokens, "output": output_tokens, "cached": 0},
            "tokens_saved": record.tokens_saved,
            "cost_usd": 0.0,
        }
