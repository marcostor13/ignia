"""
Email client — Gmail SMTP.

Server:  smtp.gmail.com
Port:    587 (STARTTLS)
Env vars:
  EMAIL_SMTP   = tucuenta@gmail.com
  APPPASSWORD  = App Password de 16 caracteres generado en myaccount.google.com
"""

import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib

logger = logging.getLogger(__name__)

_SMTP_HOST = "smtp.gmail.com"
_SMTP_PORT = 587


class EmailClient:

    # ── Core send ─────────────────────────────────────────────────────────────

    async def send(self, to: str, subject: str, html: str) -> bool:
        # Read env vars lazily so dotenv is guaranteed to have loaded first
        from_addr = os.getenv("EMAIL_SMTP", "")
        password  = os.getenv("APPPASSWORD", "")

        if not from_addr or not password:
            print(f"[email] NOT CONFIGURED — EMAIL_SMTP={repr(from_addr)} APPPASSWORD={'set' if password else 'missing'}")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = f"Ignia <{from_addr}>"
            msg["To"]      = to
            msg.attach(MIMEText(html, "html", "utf-8"))

            print(f"[email] sending → {to} via {from_addr}")
            await aiosmtplib.send(
                msg,
                hostname=_SMTP_HOST,
                port=_SMTP_PORT,
                start_tls=True,
                username=from_addr,
                password=password,
            )
            print(f"[email] sent OK → {to} | {subject}")
            return True
        except Exception as exc:
            import traceback
            print(f"[email] FAILED → {to} | {type(exc).__name__}: {exc}")
            traceback.print_exc()
            return False

    # ── Business emails ───────────────────────────────────────────────────────

    async def send_confirmation_to_lead(self, email: str, name: Optional[str] = None) -> bool:
        """Confirmation email sent to the registered lead."""
        first = name.split()[0] if name else "ahí"
        community_url = os.getenv("WHATSAPP_COMMUNITY_URL", "")
        wa_block = (
            f'<p style="margin:0 0 8px;">'
            f'<a href="{community_url}" style="color:#FF6035;font-weight:700;">Unirme a la comunidad de WhatsApp →</a>'
            f'</p>'
        ) if community_url else ""

        html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f6f6fb;font-family:'Helvetica Neue',Arial,sans-serif;color:#0D0D1A;">
<div style="max-width:560px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

  <!-- Header -->
  <div style="background:#0D0D1A;padding:24px 40px 0;">
    <img src="https://ignia.site/Satochi.png" alt="Ignia" height="32" style="display:block;margin-bottom:24px;" />
  </div>
  <div style="background:linear-gradient(135deg,#FF6035,#FF3A5C);padding:32px 40px;">
    <p style="margin:0 0 6px;color:rgba(255,255,255,0.75);font-size:13px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;">Taller Gratuito</p>
    <h1 style="margin:0;color:#fff;font-size:24px;font-weight:800;line-height:1.2;">🎉 ¡Tu cupo está reservado!</h1>
  </div>

  <!-- Body -->
  <div style="padding:36px 40px;">
    <p style="margin:0 0 20px;font-size:15px;line-height:1.7;color:#333;">
      Hola <strong>{first}</strong>, confirmamos tu inscripción al:
    </p>

    <div style="background:#f6f6fb;border-radius:12px;padding:20px 24px;margin-bottom:28px;border-left:4px solid #FF6035;">
      <p style="margin:0 0 4px;font-size:17px;font-weight:800;color:#0D0D1A;line-height:1.3;">
        De Cero a IA: Implementa Inteligencia Artificial<br>en tu Negocio en 1 Día
      </p>
      <p style="margin:6px 0 0;font-size:13px;color:#6B6B8A;">Taller gratuito en vivo · Online · Solo 30 cupos</p>
    </div>

    <p style="margin:0 0 10px;font-size:14px;font-weight:700;color:#0D0D1A;">Próximos pasos:</p>
    <ol style="margin:0 0 24px;padding-left:20px;color:#555;font-size:14px;line-height:2;">
      <li>Unite a nuestra comunidad de WhatsApp — ahí enviamos el link y los recordatorios</li>
      <li>Prepará tu laptop con internet y una cuenta de Google activa</li>
      <li>Llegá 10 minutos antes de que empiece</li>
    </ol>

    {wa_block}

    <p style="margin:24px 0 0;font-size:13px;color:#6B6B8A;line-height:1.6;">
      ¿Preguntas? Respondé este email o escribinos a
      <a href="mailto:{self.from_addr}" style="color:#FF6035;">{self.from_addr}</a>
    </p>
  </div>

  <!-- Footer -->
  <div style="padding:20px 40px;border-top:1px solid #eee;text-align:center;">
    <p style="margin:0;font-size:12px;color:#aaa;">© 2025 Ignia · Desarrollo web e IA a medida</p>
  </div>

</div>
</body>
</html>"""

        return await self.send(
            to=email,
            subject="✅ Tu cupo está reservado — Taller De Cero a IA | Ignia",
            html=html,
        )

    async def notify_team_new_lead(
        self, email: str, name: Optional[str] = None, source: str = "taller_ia"
    ) -> bool:
        """Internal notification sent to admin@ignia.site for every new lead."""
        labels = {"taller_ia": "Taller De Cero a IA", "taller": "Taller Gratuito"}
        source_label = labels.get(source, source)
        name_row = (
            f"<tr><td style='padding:7px 0;color:#6B6B8A;font-size:13px;width:90px;'>Nombre</td>"
            f"<td style='padding:7px 0;font-size:13px;font-weight:600;'>{name}</td></tr>"
        ) if name else ""

        html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f6f6fb;font-family:'Helvetica Neue',Arial,sans-serif;color:#0D0D1A;">
<div style="max-width:500px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

  <div style="background:#0D0D1A;padding:28px 36px;">
    <h1 style="margin:0;color:#fff;font-size:18px;font-weight:800;">🔔 Nuevo lead — {source_label}</h1>
  </div>

  <div style="padding:32px 36px;">
    <table style="width:100%;border-collapse:collapse;">
      <tr><td style='padding:7px 0;color:#6B6B8A;font-size:13px;width:90px;'>Email</td>
          <td style='padding:7px 0;font-size:13px;font-weight:600;'>{email}</td></tr>
      {name_row}
      <tr><td style='padding:7px 0;color:#6B6B8A;font-size:13px;'>Fuente</td>
          <td style='padding:7px 0;font-size:13px;font-weight:600;'>{source_label}</td></tr>
    </table>

    <div style="margin-top:24px;padding:14px 18px;background:#fff8f6;border-radius:10px;border:1px solid rgba(255,96,53,0.25);">
      <p style="margin:0;font-size:13px;color:#FF6035;font-weight:700;">¡Contactalo cuanto antes para cerrar la oportunidad! 🚀</p>
    </div>
  </div>

</div>
</body>
</html>"""

        return await self.send(
            to=self.from_addr,
            subject=f"🔔 Nuevo lead: {email} — {source_label}",
            html=html,
        )


email_client = EmailClient()
