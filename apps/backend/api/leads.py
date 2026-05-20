"""
Lead capture API — POST /api/leads
Saves lead to MongoDB, sends confirmation email to lead,
notifies Ignia team via email + WhatsApp Cloud API.
"""

import logging
import os
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, field_validator

from ..models.lead import lead_store
from ..whatsapp.client import whatsapp
from ..email_service.client import email_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/leads", tags=["leads"])


# ── Request / Response models ────────────────────────────────────────────────

class LeadIn(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    source: str = "taller"

    @field_validator("name", "phone", mode="before")
    @classmethod
    def strip_or_none(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v if v else None
        return v


class LeadOut(BaseModel):
    success: bool
    already_registered: bool
    message: str
    whatsapp_community_url: str


# ── Background notifications ──────────────────────────────────────────────────

async def _notify_all(email: str, name: Optional[str], phone: Optional[str], source: str) -> None:
    import asyncio

    # Run email notifications concurrently
    results = await asyncio.gather(
        email_client.send_confirmation_to_lead(email=email, name=name),
        email_client.notify_team_new_lead(email=email, name=name, source=source),
        return_exceptions=True,
    )
    for i, r in enumerate(results):
        label = ["confirmation_email", "team_email"][i]
        if isinstance(r, Exception):
            print(f"[leads] {label} raised: {type(r).__name__}: {r}")
        else:
            print(f"[leads] {label} sent={r}")

    # WhatsApp notifications (non-critical)
    try:
        wa_result = await whatsapp.notify_new_lead(email=email, name=name, source=source)
        if "error" in wa_result or wa_result.get("skipped"):
            print(f"[leads] whatsapp team notify skipped/failed: {wa_result}")
    except Exception as e:
        print(f"[leads] whatsapp notify error: {e}")

    if phone:
        try:
            await whatsapp.send_welcome_to_lead(phone=phone, name=name)
        except Exception as e:
            print(f"[leads] whatsapp welcome error: {e}")

    await lead_store.mark_notified(email=email)


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("", response_model=LeadOut, status_code=201)
async def create_lead(body: LeadIn) -> LeadOut:
    print(f"[leads] POST /api/leads — email={body.email} source={body.source}")
    try:
        lead, is_new = await lead_store.upsert(
            email=body.email,
            name=body.name,
            phone=body.phone,
            source=body.source,
        )
        print(f"[leads] upsert ok — email={lead.email} is_new={is_new}")
    except Exception as exc:
        import traceback
        print(f"[leads] DB ERROR: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error al guardar el registro.")

    if is_new:
        print(f"[leads] nuevo lead — iniciando notificaciones")
        await _notify_all(
            email=lead.email,
            name=lead.name,
            phone=lead.phone,
            source=lead.source,
        )
    else:
        print(f"[leads] lead ya existía — sin notificaciones")

    community_url = os.getenv("WHATSAPP_COMMUNITY_URL", "")

    return LeadOut(
        success=True,
        already_registered=not is_new,
        message=(
            "¡Tu lugar está reservado! Te esperamos en la comunidad."
            if is_new
            else "¡Ya estás registrado! Únete a la comunidad de WhatsApp."
        ),
        whatsapp_community_url=community_url,
    )


@router.get("")
async def list_leads(limit: int = 100) -> dict:
    """Admin endpoint — list all captured leads."""
    leads = await lead_store.all(limit=limit)
    total = await lead_store.count()
    return {
        "total": total,
        "leads": [l.to_dict() for l in leads],
    }


# ── WhatsApp webhook ──────────────────────────────────────────────────────────

@router.get("/webhook")
async def whatsapp_webhook_verify(
    hub_mode: str = "",
    hub_verify_token: str = "",
    hub_challenge: str = "",
) -> int:
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "ignia_verify_2024")
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info("WhatsApp webhook verified.")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.post("/webhook")
async def whatsapp_webhook_receive(payload: dict) -> dict:
    logger.info("WhatsApp webhook payload: %s", payload)
    return {"status": "ok"}
