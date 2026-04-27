from unittest.mock import AsyncMock, MagicMock

import pytest

from src.jarvis.llm.gateway import LLMGateway
from src.jarvis.llm.providers.base import LLMProvider, LLMResponse
from src.jarvis.llm.router import ModelRouter


class MockProvider(LLMProvider):
    """Mock LLM provider that returns canned responses."""

    def __init__(self, response_text: str = "Mock response"):
        self.response_text = response_text
        self.complete_calls = []
        self.embed_calls = []

    async def complete(self, messages, model, temperature=0.7, max_tokens=4096, stream=False):
        self.complete_calls.append({"messages": messages, "model": model, "stream": stream})
        return LLMResponse(content=self.response_text, model=model, usage={})

    async def embed(self, text, model):
        self.embed_calls.append({"text": text, "model": model})
        return [0.1] * 384  # fake embedding

    async def health_check(self):
        return True


@pytest.fixture
def mock_provider():
    return MockProvider()


@pytest.fixture
def mock_gateway(mock_provider):
    models_config = {
        "models": {
            "default": {
                "primary": {"provider": "mock", "model": "mock-model"},
            },
            "embedding": {
                "primary": {"provider": "mock", "model": "mock-embed"},
            },
        }
    }
    router = ModelRouter(models_config, {"mock": mock_provider})
    return LLMGateway(router)


@pytest.fixture
def classifier_provider():
    """Provider that returns intent classifications."""
    return MockProvider(response_text="general")
