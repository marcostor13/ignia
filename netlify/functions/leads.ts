import { MongoClient, type Collection } from "mongodb";
import nodemailer from "nodemailer";

// Reuse connection across warm invocations
let _col: Collection | null = null;
async function getCol(): Promise<Collection> {
  if (!_col) {
    const uri = process.env.MONGOURI;
    if (!uri) throw new Error("MONGOURI not set");
    const client = new MongoClient(uri);
    await client.connect();
    _col = client.db("ignia").collection("leads");
    await _col.createIndex("email", { unique: true });
    console.log("[leads] MongoDB connected");
  }
  return _col;
}

async function sendEmail(to: string, subject: string, html: string): Promise<void> {
  const user = process.env.EMAIL_SMTP;
  const pass = process.env.APPPASSWORD;
  if (!user || !pass) { console.log("[email] not configured"); return; }
  try {
    const t = nodemailer.createTransport({ host: "smtp.gmail.com", port: 587, secure: false, auth: { user, pass } });
    await t.sendMail({ from: `Ignia <${user}>`, to, subject, html });
    console.log(`[email] sent → ${to}`);
  } catch (err) {
    console.error(`[email] failed → ${to}:`, err);
  }
}

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};

export default async (req: Request) => {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });

  if (req.method === "GET") {
    const col = await getCol();
    const leads = await col.find({}).sort({ _id: -1 }).limit(100).toArray();
    return Response.json({ total: leads.length, leads }, { headers: CORS });
  }

  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });

  let body: any;
  try { body = await req.json(); } catch {
    return Response.json({ detail: "Invalid JSON" }, { status: 400 });
  }

  const email = (body.email ?? "").toLowerCase().trim();
  const name: string | null = body.name?.trim() || null;
  const phone: string | null = body.phone?.trim() || null;
  const source: string = body.source ?? "taller";

  if (!email) return Response.json({ detail: "Email requerido" }, { status: 400 });

  console.log(`[leads] POST — email=${email} source=${source}`);

  try {
    const col = await getCol();
    const existing = await col.findOne({ email });

    if (existing) {
      console.log(`[leads] ya existe: ${email}`);
      return Response.json({
        success: true, already_registered: true,
        message: "¡Ya estás registrado! Únete a la comunidad de WhatsApp.",
        whatsapp_community_url: process.env.WHATSAPP_COMMUNITY_URL ?? "",
      }, { status: 201, headers: CORS });
    }

    await col.insertOne({
      email, name, phone, source,
      whatsapp_notified: false, email_sent: false,
      created_at: new Date().toISOString(),
    });
    console.log(`[leads] guardado: ${email}`);

    // Send emails concurrently
    const first = name?.split(" ")[0] ?? "ahí";
    const waUrl = process.env.WHATSAPP_COMMUNITY_URL ?? "";
    const waBlock = waUrl
      ? `<p style="margin:0 0 8px;"><a href="${waUrl}" style="color:#FF6035;font-weight:700;">Unirme a la comunidad de WhatsApp →</a></p>`
      : "";

    const confirmHtml = `<!DOCTYPE html><html lang="es"><body style="margin:0;padding:0;background:#f6f6fb;font-family:'Helvetica Neue',Arial,sans-serif;">
<div style="max-width:560px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;">
  <div style="background:#0D0D1A;padding:24px 40px 0;">
    <img src="https://ignia.site/Satochi.png" alt="Ignia" height="32" style="display:block;margin-bottom:24px;" />
  </div>
  <div style="background:linear-gradient(135deg,#FF6035,#FF3A5C);padding:32px 40px;">
    <p style="margin:0 0 6px;color:rgba(255,255,255,0.75);font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;">Taller Gratuito</p>
    <h1 style="margin:0;color:#fff;font-size:24px;font-weight:800;">🎉 ¡Tu cupo está reservado!</h1>
  </div>
  <div style="padding:36px 40px;">
    <p style="margin:0 0 20px;font-size:15px;line-height:1.7;color:#333;">Hola <strong>${first}</strong>, confirmamos tu inscripción al taller <strong>De Cero a IA: Implementa Inteligencia Artificial en tu Negocio en 1 Día</strong>.</p>
    <p style="margin:0 0 10px;font-size:14px;font-weight:700;color:#0D0D1A;">Próximos pasos:</p>
    <ol style="margin:0 0 24px;padding-left:20px;color:#555;font-size:14px;line-height:2;">
      <li>Únete a nuestra comunidad de WhatsApp — ahí enviamos el link y los recordatorios</li>
      <li>Prepara tu laptop con internet y una cuenta de Google activa</li>
      <li>Llega 10 minutos antes de que empiece</li>
    </ol>
    ${waBlock}
    <p style="margin:24px 0 0;font-size:13px;color:#6B6B8A;">¿Preguntas? Escríbenos a <a href="mailto:admin@ignia.site" style="color:#FF6035;">admin@ignia.site</a></p>
  </div>
  <div style="padding:20px 40px;border-top:1px solid #eee;text-align:center;">
    <p style="margin:0;font-size:12px;color:#aaa;">© 2025 Ignia · Desarrollo web e IA a medida</p>
  </div>
</div></body></html>`;

    const teamHtml = `<p><b>Email:</b> ${email}</p><p><b>Nombre:</b> ${name ?? "—"}</p><p><b>Teléfono:</b> ${phone ?? "—"}</p><p><b>Fuente:</b> ${source}</p>`;

    await Promise.all([
      sendEmail(email, "✅ Tu cupo está reservado — Taller De Cero a IA | Ignia", confirmHtml),
      sendEmail(process.env.EMAIL_SMTP!, `🔔 Nuevo lead: ${email}`, teamHtml),
    ]);

    await col.updateOne({ email }, { $set: { email_sent: true } });

    return Response.json({
      success: true, already_registered: false,
      message: "¡Tu lugar está reservado! Te esperamos en la comunidad.",
      whatsapp_community_url: waUrl,
    }, { status: 201, headers: CORS });
  } catch (err) {
    console.error("[leads] error:", err);
    return Response.json({ detail: "Error al guardar el registro." }, { status: 500, headers: CORS });
  }
};

export const config = { path: "/api/leads" };
