"""
Lead capture API — POST /api/leads
Saves lead to MongoDB, sends confirmation email to lead,
notifies Ignia team via email + WhatsApp Cloud API.
"""

import logging
import os
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
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
    """Runs after the HTTP response is sent. Fires all notifications in parallel-ish."""

    # 1. Confirmation email to lead
    await email_client.send_confirmation_to_lead(email=email, name=name)

    # 2. Internal notification email to team
    await email_client.notify_team_new_lead(email=email, name=name, source=source)

    # 3. WhatsApp notification to team
    wa_result = await whatsapp.notify_new_lead(email=email, name=name, source=source)
    if "error" in wa_result or wa_result.get("skipped"):
        logger.warning("WhatsApp team notify skipped/failed: %s", wa_result)

    # 4. WhatsApp welcome to lead (only if they gave their phone)
    if phone:
        await whatsapp.send_welcome_to_lead(phone=phone, name=name)

    # 5. Mark as notified in DB
    await lead_store.mark_notified(email=email)


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("", response_model=LeadOut, status_code=201)
async def create_lead(body: LeadIn, background_tasks: BackgroundTasks) -> LeadOut:
    lead, is_new = await lead_store.upsert(
        email=body.email,
        name=body.name,
        phone=body.phone,
        source=body.source,
    )

    if is_new:
        background_tasks.add_task(
            _notify_all,
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
