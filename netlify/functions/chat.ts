import OpenAI from "openai";

const MODEL = process.env.OPENAI_MODEL ?? "gpt-4.1-mini";
const CALENDAR_TRIGGER = "__OPEN_CALENDAR__";

const SYSTEM_PROMPT = `Eres el asistente de ventas de Ignia, empresa de desarrollo de software a medida en Perú.

SOBRE IGNIA:
- Plataformas web, apps móviles, ERPs, CRMs, integraciones con IA
- Stack: Angular, React, Python, FastAPI, NestJS, MongoDB, PostgreSQL, AWS
- Casos reales: AsisteYa (ERP+biometría), Viatika (viáticos), Redline (USA), BA Kitchen (IA+iOS+Stripe)
- Sprints de 2 semanas, demos reales, soporte post-lanzamiento

REGLAS ESTRICTAS:
- Responde SOLO en español
- Máximo 2 oraciones por respuesta
- NUNCA repitas preguntas que ya fueron respondidas en la conversación
- NUNCA saludes de nuevo si ya saludaste
- No inventes precios ni plazos
- Sé directo: responde la pregunta y avanza con UNA sola pregunta siguiente

FLUJO DE AGENDA (cuando el usuario quiera reunirse, hablar, cotizar o agendar):
- Llama a open_calendar inmediatamente. No pidas datos previos, el formulario los recopila.
- Después de llamar a open_calendar, di: "Te abrí el calendario, elige el horario que mejor te funcione."

REGLAS CRÍTICAS:
- NUNCA digas que una reunión fue agendada, solo que abriste el calendario
- NUNCA pidas nombre, email u horario antes de llamar a open_calendar
- Si el usuario tiene preguntas de negocio, respóndelas brevemente antes de ofrecer agendar`;

// Per-instance rate limiting
const _ipLog = new Map<string, number[]>();
function allowRequest(ip: string): boolean {
  const now = Date.now();
  const window = 3_600_000;
  const limit = Number(process.env.CHAT_RATE_LIMIT ?? "20");
  const hits = (_ipLog.get(ip) ?? []).filter((t) => now - t < window);
  if (hits.length >= limit) return false;
  _ipLog.set(ip, [...hits, now]);
  return true;
}

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

export default async (req: Request) => {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });

  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  if (!allowRequest(ip)) {
    return Response.json(
      { detail: "Demasiadas solicitudes. Por favor espera unos minutos." },
      { status: 429, headers: CORS }
    );
  }

  let body: any;
  try { body = await req.json(); } catch {
    return Response.json({ detail: "Invalid JSON" }, { status: 400 });
  }

  const { message, conversation_history = [] } = body;
  if (!message) return Response.json({ detail: "message required" }, { status: 400 });

  const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  const today = new Date().toLocaleDateString("en-CA", { timeZone: "America/Lima" });
  const systemMsg = `${SYSTEM_PROMPT}\n\nFECHA DE HOY: ${today} (Lima UTC-5). Convierte 'mañana', 'hoy', 'el lunes' a fechas reales.`;

  const messages: OpenAI.ChatCompletionMessageParam[] = [
    { role: "system", content: systemMsg },
    ...conversation_history,
    { role: "user", content: message },
  ];

  const tools: OpenAI.ChatCompletionTool[] = [{
    type: "function",
    function: {
      name: "open_calendar",
      description: "Abre el calendario de reservas de Ignia para que el usuario pueda elegir un horario y agendar directamente.",
      parameters: { type: "object", properties: {}, required: [] },
    },
  }];

  try {
    const resp = await client.chat.completions.create({
      model: MODEL, messages, max_tokens: 512, temperature: 0.7, tools, tool_choice: "auto",
    });

    const msg = resp.choices[0].message;
    let responseText = "";
    let action: string | null = null;

    if (msg.tool_calls?.length) {
      for (const tc of msg.tool_calls) {
        if (tc.function.name === "open_calendar") action = "open_calendar";
      }
      messages.push({ role: "assistant", content: msg.content, tool_calls: msg.tool_calls });
      for (const tc of msg.tool_calls) {
        messages.push({ role: "tool", tool_call_id: tc.id, content: CALENDAR_TRIGGER });
      }
      const followup = await client.chat.completions.create({
        model: MODEL, messages, max_tokens: 512, temperature: 0.7,
      });
      responseText = followup.choices[0].message.content ?? "";
    } else {
      responseText = msg.content ?? "";
    }

    return Response.json(
      { response: responseText, action, agent_id: "website_agent", tokens_used: {}, tokens_saved: 0, cost_usd: 0 },
      { headers: CORS }
    );
  } catch (err: any) {
    console.error("[chat]", err?.message ?? err);
    return Response.json(
      { response: "Lo siento, hubo un error técnico. Escríbenos a admin@ignia.site", action: null, agent_id: "website_agent", tokens_used: {}, tokens_saved: 0, cost_usd: 0 },
      { headers: CORS }
    );
  }
};

export const config = { path: "/api/chat" };
