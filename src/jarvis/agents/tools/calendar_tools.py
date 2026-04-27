from datetime import datetime, timedelta, timezone

from langchain_core.tools import tool

from config.settings import settings
from src.jarvis.google.auth import GoogleAuth
from src.jarvis.google.calendar import CalendarClient


def _get_calendar_client() -> CalendarClient:
    auth = GoogleAuth(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        tokens_dir=settings.tokens_dir,
    )
    creds = auth.get_credentials()
    if not creds:
        raise RuntimeError("Google account not authenticated. Run 'jarvis auth login' first.")
    return CalendarClient(creds)


def _format_event(event) -> str:
    time_str = event.start.strftime("%H:%M") + " - " + event.end.strftime("%H:%M")
    parts = [f"- {time_str} | {event.summary}"]
    if event.location:
        parts.append(f"  Location: {event.location}")
    if event.meet_link:
        parts.append(f"  Meet: {event.meet_link}")
    if event.attendees:
        parts.append(f"  Attendees: {', '.join(event.attendees[:5])}")
    return "\n".join(parts)


@tool
def get_events_today() -> str:
    """Get all calendar events for today."""
    client = _get_calendar_client()
    events = client.get_events_today()
    if not events:
        return "No events scheduled for today."
    return "\n\n".join(_format_event(e) for e in events)


@tool
def get_upcoming_events(minutes: int = 60) -> str:
    """Get calendar events starting within the next N minutes."""
    client = _get_calendar_client()
    events = client.get_upcoming(minutes=minutes)
    if not events:
        return f"No events in the next {minutes} minutes."
    return "\n\n".join(_format_event(e) for e in events)


@tool
def get_events_this_week() -> str:
    """Get all calendar events for the current week (Mon-Sun)."""
    client = _get_calendar_client()
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=now.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    events = client.get_events_range(start, end)
    if not events:
        return "No events scheduled this week."

    # Group by day
    by_day: dict[str, list] = {}
    for e in events:
        day = e.start.strftime("%A %b %d")
        by_day.setdefault(day, []).append(e)

    lines = []
    for day, day_events in by_day.items():
        lines.append(f"\n**{day}**")
        for e in day_events:
            lines.append(_format_event(e))
    return "\n".join(lines)


@tool
def check_calendar_conflicts(start_time: str, end_time: str) -> str:
    """Check for calendar conflicts in a time range. Times in ISO format (e.g., '2024-01-15T10:00:00')."""
    client = _get_calendar_client()
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    conflicts = client.check_conflicts(start, end)
    if not conflicts:
        return "No conflicts found in that time range."
    return "Conflicts found:\n" + "\n\n".join(_format_event(e) for e in conflicts)
