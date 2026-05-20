"""
ScheduleMeetingSkill: creates a calendar event in Outlook via Microsoft Graph API.

Env vars required:
  MS_TENANT_ID       — Azure / Entra ID tenant ID
  MS_CLIENT_ID       — App registration client ID
  MS_CLIENT_SECRET   — App registration client secret
  MS_USER_EMAIL      — Outlook email whose calendar receives the event

The Azure app needs Application permission: Calendars.ReadWrite (admin-consented).
"""

import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx

from .base_skill import BaseSkill, SkillResult

_GRAPH = "https://graph.microsoft.com/v1.0"
_TZ = ZoneInfo("America/Lima")


class ScheduleMeetingSkill(BaseSkill):
    name = "schedule_meeting"
    description = (
        "Agenda una reunión en el calendario de Outlook de Ignia y envía una invitación "
        "al cliente. Usar solo cuando se tengan: nombre completo, email, fecha (YYYY-MM-DD), "
        "hora (HH:MM en formato 24h) y tema de la reunión."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "attendee_name": {
                "type": "string",
                "description": "Nombre completo del cliente",
            },
            "attendee_email": {
                "type": "string",
                "description": "Email del cliente (recibirá la invitación)",
            },
            "meeting_topic": {
                "type": "string",
                "description": "Tema o proyecto a discutir en la reunión",
            },
            "date_str": {
                "type": "string",
                "description": "Fecha en formato YYYY-MM-DD (ej. 2025-06-15)",
            },
            "time_str": {
                "type": "string",
                "description": "Hora de inicio en formato HH:MM, 24h (ej. 10:00)",
            },
            "duration_minutes": {
                "type": "integer",
                "description": "Duración en minutos. Por defecto 30.",
                "default": 30,
            },
        },
        "required": ["attendee_name", "attendee_email", "meeting_topic", "date_str", "time_str"],
    }

    async def _get_token(self) -> str:
        tenant_id = os.environ["MS_TENANT_ID"]
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": os.environ["MS_CLIENT_ID"],
                    "client_secret": os.environ["MS_CLIENT_SECRET"],
                    "scope": "https://graph.microsoft.com/.default",
                },
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()["access_token"]

    async def execute(
        self,
        attendee_name: str,
        attendee_email: str,
        meeting_topic: str,
        date_str: str,
        time_str: str,
        duration_minutes: int = 30,
    ) -> SkillResult:
        try:
            start_dt = datetime.fromisoformat(f"{date_str}T{time_str}:00").replace(tzinfo=_TZ)
            end_dt = start_dt + timedelta(minutes=duration_minutes)

            token = await self._get_token()
            owner = os.environ["MS_USER_EMAIL"]

            event = {
                "subject": f"Ignia — {meeting_topic}",
                "body": {
                    "contentType": "HTML",
                    "content": (
                        f"<p>Reunión con <strong>{attendee_name}</strong> ({attendee_email}).</p>"
                        f"<p><strong>Tema:</strong> {meeting_topic}</p>"
                        f"<p><em>Agendada desde el asistente virtual de ignia.site</em></p>"
                    ),
                },
                "start": {
                    "dateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "timeZone": "America/Lima",
                },
                "end": {
                    "dateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "timeZone": "America/Lima",
                },
                "attendees": [
                    {
                        "emailAddress": {"address": attendee_email, "name": attendee_name},
                        "type": "required",
                    }
                ],
                "isOnlineMeeting": True,
                "onlineMeetingProvider": "teamsForBusiness",
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{_GRAPH}/users/{owner}/calendar/events",
                    json=event,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()

            join_url = (data.get("onlineMeeting") or {}).get("joinUrl", "")
            date_display = start_dt.strftime("%d/%m/%Y a las %H:%M")

            return SkillResult(
                success=True,
                data={
                    "message": (
                        f"Reunión agendada para el {date_display} (hora Lima). "
                        f"Se envió una invitación a {attendee_email}."
                        + (f" Link de Teams: {join_url}" if join_url else "")
                    ),
                    "event_id": data.get("id"),
                    "start": start_dt.isoformat(),
                    "join_url": join_url,
                },
            )

        except KeyError as exc:
            msg = f"Variable de entorno faltante: {exc}"
            print(f"[ScheduleMeetingSkill] {msg}")
            return SkillResult(success=False, data=msg)
        except httpx.HTTPStatusError as exc:
            msg = f"Graph API error {exc.response.status_code}: {exc.response.text}"
            print(f"[ScheduleMeetingSkill] {msg}")
            return SkillResult(success=False, data=msg)
        except ValueError as exc:
            msg = f"Fecha u hora inválida: {exc}. Asegúrate de usar date_str=YYYY-MM-DD y time_str=HH:MM"
            print(f"[ScheduleMeetingSkill] {msg}")
            return SkillResult(success=False, data=msg)
        except Exception as exc:
            import traceback; traceback.print_exc()
            return SkillResult(success=False, data=str(exc))
