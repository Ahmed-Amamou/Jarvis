from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from src.jarvis.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """Health endpoint should return even if Ollama is unreachable."""
    with patch("src.jarvis.api.routers.health.get_llm_gateway") as mock:
        mock_gw = mock.return_value
        mock_gw.router.resolve.return_value = []
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "version" in data


def test_auth_status_endpoint(client):
    with patch("src.jarvis.api.routers.auth._google_auth") as mock_auth:
        mock_auth.is_authenticated.return_value = False
        resp = client.get("/auth/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "google_authenticated" in data
