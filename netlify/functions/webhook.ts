export default async (req: Request) => {
  const url = new URL(req.url);
  const verifyToken = process.env.WHATSAPP_VERIFY_TOKEN ?? "ignia_verify_2024";

  if (req.method === "GET") {
    const mode = url.searchParams.get("hub.mode");
    const token = url.searchParams.get("hub.verify_token");
    const challenge = url.searchParams.get("hub.challenge");
    if (mode === "subscribe" && token === verifyToken) {
      return new Response(challenge ?? "", { status: 200 });
    }
    return new Response("Forbidden", { status: 403 });
  }

  if (req.method === "POST") {
    return Response.json({ status: "ok" });
  }

  return new Response("Method not allowed", { status: 405 });
};

export const config = { path: "/api/leads/webhook" };
