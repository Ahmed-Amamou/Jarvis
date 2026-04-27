from langchain_core.tools import BaseTool

from .base import BaseAgent
from .tools.calendar_tools import (
    check_calendar_conflicts,
    get_events_today,
    get_events_this_week,
    get_upcoming_events,
)

SYSTEM_PROMPT = """You are the Calendar Agent for JARVIS. Your job is to help the user manage their schedule.

You have access to tools for reading Google Calendar events.
When presenting events, format them clearly with time, title, and relevant details.
For meeting reminders, include the meeting link if available.
Flag any scheduling conflicts proactively."""


class CalendarAgent(BaseAgent):
    @property
    def agent_id(self) -> str:
        return "calendar_agent"

    def get_tools(self) -> list[BaseTool]:
        return [
            get_events_today,
            get_upcoming_events,
            get_events_this_week,
            check_calendar_conflicts,
        ]

    def get_system_prompt(self) -> str:
        return SYSTEM_PROMPT
