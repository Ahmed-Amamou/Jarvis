import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    id: str
    summary: str
    start: datetime
    end: datetime
    location: str
    attendees: list[str]
    meet_link: str
    description: str
    status: str


class CalendarClient:
    def __init__(self, credentials: Credentials):
        self.service = build("calendar", "v3", credentials=credentials)

    def get_events_today(self) -> list[CalendarEvent]:
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        return self._get_events(start_of_day, end_of_day)

    def get_events_range(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        return self._get_events(start, end)

    def get_upcoming(self, minutes: int = 30) -> list[CalendarEvent]:
        """Get events starting within the next N minutes."""
        now = datetime.now(timezone.utc)
        end = now + timedelta(minutes=minutes)
        return self._get_events(now, end)

    def check_conflicts(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        """Check if there are any events overlapping with the given time range."""
        return self._get_events(start, end)

    def _get_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=start.isoformat(),
                timeMax=end.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = []
        for item in events_result.get("items", []):
            start_dt = self._parse_event_time(item.get("start", {}))
            end_dt = self._parse_event_time(item.get("end", {}))

            attendees = [
                a.get("email", "") for a in item.get("attendees", [])
            ]

            events.append(
                CalendarEvent(
                    id=item["id"],
                    summary=item.get("summary", "(No title)"),
                    start=start_dt,
                    end=end_dt,
                    location=item.get("location", ""),
                    attendees=attendees,
                    meet_link=item.get("hangoutLink", ""),
                    description=item.get("description", ""),
                    status=item.get("status", "confirmed"),
                )
            )
        return events

    def _parse_event_time(self, time_info: dict) -> datetime:
        dt_str = time_info.get("dateTime")
        if dt_str:
            return datetime.fromisoformat(dt_str)
        # All-day event
        date_str = time_info.get("date", "")
        return datetime.fromisoformat(date_str) if date_str else datetime.now(timezone.utc)
