"""
Lead capture API — POST /api/leads
Saves lead to SQLite, notifies Ignia team via WhatsApp Cloud API.
"""

import logging
import os
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr, field_validator

from ..models.lead import lead_store
from ..whatsapp.client import whatsapp

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/leads", tags=["leads"])


# ── Request / Response models ────────────────────────────────────────────────

class LeadIn(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None          # optional — to send them a WA welcome message
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


# ── Background tasks ─────────────────────────────────────────────────────────

async def _notify_and_welcome(lead_id: int, email: str, name: Optional[str], phone: Optional[str], source: str) -> None:
    """Run after the HTTP response is sent."""
    # 1. Notify team
    result = await whatsapp.notify_new_lead(email=email, name=name, source=source)
    if "error" not in result and not result.get("skipped"):
        lead_store.mark_notified(lead_id)
        logger.info("Team notified via WhatsApp for lead %s", lead_id)
    else:
        logger.warning("WhatsApp notify skipped/failed for lead %s: %s", lead_id, result)

    # 2. Welcome the lead if they gave their phone
    if phone:
        await whatsapp.send_welcome_to_lead(phone=phone, name=name)


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("", response_model=LeadOut, status_code=201)
async def create_lead(body: LeadIn, background_tasks: BackgroundTasks) -> LeadOut:
    """
    Register a lead for the free workshop.
    - Persists to SQLite
    - Triggers WhatsApp notification to the Ignia team (background)
    - Returns the WhatsApp community URL
    """
    lead, is_new = lead_store.upsert(
        email=body.email,
        name=body.name,
        phone=body.phone,
        source=body.source,
    )

    if is_new:
        background_tasks.add_task(
            _notify_and_welcome,
            lead_id=lead.id,
            email=lead.email,
            name=lead.name,
            phone=lead.phone,
            source=lead.source,
        )

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
    leads = lead_store.all(limit=limit)
    return {
        "total": lead_store.count(),
        "leads": [l.to_dict() for l in leads],
    }


# ── WhatsApp webhook (for receiving messages / Meta verification) ─────────────

@router.get("/webhook")
async def whatsapp_webhook_verify(
    hub_mode: str = "",
    hub_verify_token: str = "",
    hub_challenge: str = "",
) -> int:
    """
    Meta webhook verification endpoint.
    Set this URL in Meta Business Manager → WhatsApp → Webhooks.
    WHATSAPP_VERIFY_TOKEN must match what you set in Meta.
    """
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "ignia_verify_2024")
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info("WhatsApp webhook verified.")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.post("/webhook")
async def whatsapp_webhook_receive(payload: dict) -> dict:
    """Receive incoming WhatsApp messages/status updates."""
    logger.info("WhatsApp webhook payload: %s", payload)
    return {"status": "ok"}
