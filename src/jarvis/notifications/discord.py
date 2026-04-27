import logging

import httpx

logger = logging.getLogger(__name__)


class DiscordNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, title: str, message: str, color: int = 0x5865F2) -> bool:
        """Send a Discord embed message via webhook."""
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured")
            return False

        payload = {
            "embeds": [
                {
                    "title": title,
                    "description": message[:4096],
                    "color": color,
                }
            ]
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.webhook_url, json=payload)
            if resp.status_code in (200, 204):
                logger.info(f"Discord notification sent: {title}")
                return True
            else:
                logger.error(f"Discord webhook failed: {resp.status_code} {resp.text}")
                return False

    async def send_plain(self, message: str) -> bool:
        """Send a plain text message via webhook."""
        if not self.webhook_url:
            return False

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.webhook_url, json={"content": message[:2000]})
            return resp.status_code in (200, 204)
