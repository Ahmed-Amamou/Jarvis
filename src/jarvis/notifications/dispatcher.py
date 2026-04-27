import logging
from dataclasses import dataclass

from config.settings import settings
from .discord import DiscordNotifier
from .whatsapp import WhatsAppNotifier

logger = logging.getLogger(__name__)


@dataclass
class Notification:
    title: str
    message: str
    notification_type: str  # meeting_reminder, daily_summary, urgent_email, email_digest


class NotificationDispatcher:
    def __init__(self):
        self.discord = DiscordNotifier(webhook_url=settings.discord_webhook_url)
        self.whatsapp = WhatsAppNotifier(
            account_sid=settings.twilio_account_sid,
            auth_token=settings.twilio_auth_token,
            from_number=settings.whatsapp_from,
            to_number=settings.whatsapp_to,
        )

    async def dispatch(self, notification: Notification) -> dict[str, bool]:
        """Send notification to all configured channels."""
        results = {}

        # Color coding for Discord embeds
        colors = {
            "meeting_reminder": 0xFFA500,  # orange
            "urgent_email": 0xFF0000,      # red
            "daily_summary": 0x5865F2,     # blurple
            "email_digest": 0x00FF00,      # green
        }
        color = colors.get(notification.notification_type, 0x5865F2)

        if settings.discord_webhook_url:
            results["discord"] = await self.discord.send(
                title=notification.title,
                message=notification.message,
                color=color,
            )

        if settings.twilio_account_sid and settings.whatsapp_to:
            whatsapp_msg = f"*{notification.title}*\n\n{notification.message}"
            results["whatsapp"] = await self.whatsapp.send(whatsapp_msg)

        logger.info(f"Notification dispatched: {notification.title} -> {results}")
        return results
