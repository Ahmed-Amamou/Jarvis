from unittest.mock import AsyncMock, patch

import pytest

from src.jarvis.notifications.discord import DiscordNotifier
from src.jarvis.notifications.dispatcher import Notification, NotificationDispatcher


@pytest.mark.asyncio
async def test_discord_notifier_send():
    notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 204
        result = await notifier.send("Test Title", "Test message")
        assert result is True
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_discord_notifier_no_url():
    notifier = DiscordNotifier(webhook_url="")
    result = await notifier.send("Title", "Message")
    assert result is False


@pytest.mark.asyncio
async def test_discord_send_plain():
    notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        result = await notifier.send_plain("Hello JARVIS!")
        assert result is True
