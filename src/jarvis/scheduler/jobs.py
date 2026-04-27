import logging
from datetime import datetime, timezone

from config.settings import settings
from src.jarvis.google.auth import GoogleAuth
from src.jarvis.google.calendar import CalendarClient
from src.jarvis.google.gmail import GmailClient
from src.jarvis.notifications.dispatcher import Notification, NotificationDispatcher

logger = logging.getLogger(__name__)

dispatcher = NotificationDispatcher()


def _get_google_auth() -> GoogleAuth:
    return GoogleAuth(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        tokens_dir=settings.tokens_dir,
    )


async def morning_summary():
    """Daily morning summary: today's calendar + unread email count."""
    logger.info("Running morning summary job")
    auth = _get_google_auth()
    creds = auth.get_credentials()
    if not creds:
        logger.warning("Google not authenticated, skipping morning summary")
        return

    # Calendar
    cal = CalendarClient(creds)
    events = cal.get_events_today()
    if events:
        cal_summary = "\n".join(
            f"- {e.start.strftime('%H:%M')} {e.summary}" for e in events
        )
    else:
        cal_summary = "No meetings today!"

    # Email
    gmail = GmailClient(creds)
    unread = gmail.list_unread(max_results=5)
    if unread:
        email_summary = f"{len(unread)} unread emails:\n" + "\n".join(
            f"- {e.sender}: {e.subject}" for e in unread[:5]
        )
    else:
        email_summary = "Inbox zero!"

    message = f"**Schedule**\n{cal_summary}\n\n**Email**\n{email_summary}"

    await dispatcher.dispatch(
        Notification(
            title="Good Morning! Here's your daily briefing",
            message=message,
            notification_type="daily_summary",
        )
    )


async def meeting_reminder():
    """Check for meetings starting in the next 15 minutes."""
    logger.info("Checking for upcoming meetings")
    auth = _get_google_auth()
    creds = auth.get_credentials()
    if not creds:
        return

    cal = CalendarClient(creds)
    upcoming = cal.get_upcoming(minutes=15)

    for event in upcoming:
        parts = [f"**{event.summary}** starts at {event.start.strftime('%H:%M')}"]
        if event.meet_link:
            parts.append(f"Join: {event.meet_link}")
        if event.location:
            parts.append(f"Location: {event.location}")

        await dispatcher.dispatch(
            Notification(
                title="Meeting Starting Soon",
                message="\n".join(parts),
                notification_type="meeting_reminder",
            )
        )


async def email_check():
    """Check for new urgent/important emails."""
    logger.info("Checking for urgent emails")
    auth = _get_google_auth()
    creds = auth.get_credentials()
    if not creds:
        return

    gmail = GmailClient(creds)
    urgent = gmail.search_emails("is:unread is:important", max_results=3)

    if urgent:
        lines = [f"- {e.sender}: {e.subject}" for e in urgent]
        await dispatcher.dispatch(
            Notification(
                title=f"{len(urgent)} Important Unread Email(s)",
                message="\n".join(lines),
                notification_type="urgent_email",
            )
        )
