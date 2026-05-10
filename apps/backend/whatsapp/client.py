"""
WhatsApp Cloud API client (Meta official API v20.0).

Docs: https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages
"""

import os
import logging
from datetime import datetime
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

GRAPH_VERSION = "v20.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"


class WhatsAppClient:
    """
    Async client for the WhatsApp Cloud API.

    Required env vars:
      WHATSAPP_PHONE_NUMBER_ID  – e.g. "123456789012345"
      WHATSAPP_ACCESS_TOKEN     – permanent system-user token from Meta Business
      WHATSAPP_NOTIFY_PHONE     – Ignia team phone with country code, no '+' (e.g. "5491112345678")
      WHATSAPP_COMMUNITY_URL    – invite link to the WhatsApp community group
    """

    def __init__(self) -> None:
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        self.notify_phone = os.getenv("WHATSAPP_NOTIFY_PHONE", "")
        self.community_url = os.getenv("WHATSAPP_COMMUNITY_URL", "")

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    @property
    def _messages_url(self) -> str:
        return f"{GRAPH_BASE}/{self.phone_number_id}/messages"

    def is_configured(self) -> bool:
        return bool(self.phone_number_id and self.access_token and self.notify_phone)

    # ── Core send methods ────────────────────────────────────────────────────

    async def send_text(self, to: str, body: str) -> dict:
        """
        Send a free-form text message.
        Only works within a 24-hour customer-initiated window.
        For proactive messages use send_template().
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }
        return await self._post(payload)

    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "es",
        components: Optional[list] = None,
    ) -> dict:
        """
        Send a pre-approved template message.
        Works anytime (no 24-hour restriction).
        Template must be approved in Meta Business Manager.
        """
        template: dict = {
            "name": template_name,
            "language": {"code": language_code},
        }
        if components:
            template["components"] = components

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": template,
        }
        return await self._post(payload)

    async def _post(self, payload: dict) -> dict:
        if not self.is_configured():
            logger.warning("WhatsApp not configured — skipping send.")
            return {"skipped": True, "reason": "WhatsApp credentials not configured"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self._messages_url, json=payload, headers=self._headers)
                data = resp.json()
                if resp.status_code >= 400:
                    logger.error("WhatsApp API error %s: %s", resp.status_code, data)
                return data
        except Exception as exc:
            logger.error("WhatsApp send failed: %s", exc)
            return {"error": str(exc)}

    # ── Business notifications ───────────────────────────────────────────────

    async def notify_new_lead(self, email: str, name: Optional[str] = None, source: str = "taller") -> dict:
        """
        Notify the Ignia team of a new lead registration.
        Sends to WHATSAPP_NOTIFY_PHONE using a free-form text message.
        (Works because the team's number initiates the conversation or is the business number itself.)
        """
        name_line = f"👤 Nombre: {name}\n" if name else ""
        source_label = {"taller": "Taller Gratuito", "contacto": "Formulario de Contacto"}.get(source, source)
        timestamp = datetime.utcnow().strftime("%d/%m/%Y %H:%M") + " UTC"

        body = (
            f"🔔 *Nuevo lead — {source_label}*\n\n"
            f"📧 Email: {email}\n"
            f"{name_line}"
            f"📌 Fuente: {source_label}\n"
            f"🕐 {timestamp}\n\n"
            f"¡Responde cuanto antes para cerrar la oportunidad! 🚀"
        )
        return await self.send_text(self.notify_phone, body)

    async def send_welcome_to_lead(self, phone: str, name: Optional[str] = None) -> dict:
        """
        Send a welcome message to a lead who provided their phone number.
        Uses the 'ignia_bienvenida_taller' template (must be pre-approved).
        Falls back to free-form text (only works if they messaged Ignia first).
        """
        template_name = os.getenv("WHATSAPP_WELCOME_TEMPLATE", "ignia_bienvenida_taller")
        first_name = name.split()[0] if name else "ahí"

        components = [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": first_name}],
            }
        ]
        return await self.send_template(phone, template_name, components=components)


# Singleton
whatsapp = WhatsAppClient()
