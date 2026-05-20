"""
OpenCalendarSkill: triggers the booking calendar modal in the frontend.
The skill returns a special marker that the OpenAIAgent picks up
and forwards as action="open_calendar" in the ChatResponse.
"""

from .base_skill import BaseSkill, SkillResult

CALENDAR_TRIGGER = "__OPEN_CALENDAR__"


class OpenCalendarSkill(BaseSkill):
    name = "open_calendar"
    description = (
        "Abre el calendario de reservas de Ignia para que el usuario pueda elegir "
        "un horario disponible y agendar directamente. Usar cuando el usuario quiera "
        "agendar una reunión, llamada, o consulta."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Mensaje breve de confirmación para mostrar al usuario antes de abrir el calendario.",
            }
        },
        "required": [],
    }

    async def execute(self, message: str = "") -> SkillResult:
        return SkillResult(success=True, data=CALENDAR_TRIGGER)
