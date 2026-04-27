import logging

logger = logging.getLogger(__name__)


class WhatsAppNotifier:
    def __init__(self, account_sid: str, auth_token: str, from_number: str, to_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.to_number = to_number

    async def send(self, message: str) -> bool:
        """Send a WhatsApp message via Twilio API."""
        if not all([self.account_sid, self.auth_token, self.to_number]):
            logger.warning("WhatsApp (Twilio) not configured")
            return False

        try:
            from twilio.rest import Client

            client = Client(self.account_sid, self.auth_token)
            msg = client.messages.create(
                body=message[:1600],
                from_=self.from_number,
                to=self.to_number,
            )
            logger.info(f"WhatsApp message sent: {msg.sid}")
            return True
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return False
