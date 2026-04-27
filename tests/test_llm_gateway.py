import pytest

from src.jarvis.llm.gateway import LLMGateway
from src.jarvis.llm.providers.base import LLMResponse
from src.jarvis.llm.router import ModelRouter
from tests.conftest import MockProvider


@pytest.mark.asyncio
async def test_gateway_complete(mock_gateway, mock_provider):
    result = await mock_gateway.complete(
        messages=[{"role": "user", "content": "hello"}],
        model="default",
    )
    assert isinstance(result, LLMResponse)
    assert result.content == "Mock response"
    assert len(mock_provider.complete_calls) == 1


@pytest.mark.asyncio
async def test_gateway_embed(mock_gateway, mock_provider):
    result = await mock_gateway.embed("test text", model="embedding")
    assert isinstance(result, list)
    assert len(result) == 384
    assert len(mock_provider.embed_calls) == 1


@pytest.mark.asyncio
async def test_gateway_fallback():
    """Test that gateway falls back to second provider on failure."""

    class FailingProvider(MockProvider):
        async def complete(self, messages, model, **kwargs):
            raise ConnectionError("Ollama down")

    failing = FailingProvider()
    fallback = MockProvider(response_text="Fallback response")

    config = {
        "models": {
            "default": {
                "primary": {"provider": "failing", "model": "m1"},
                "fallback": {"provider": "fallback", "model": "m2"},
            },
        }
    }
    router = ModelRouter(config, {"failing": failing, "fallback": fallback})
    gateway = LLMGateway(router)

    result = await gateway.complete(
        messages=[{"role": "user", "content": "hello"}],
        model="default",
    )
    assert result.content == "Fallback response"


@pytest.mark.asyncio
async def test_gateway_all_providers_fail():
    class FailingProvider(MockProvider):
        async def complete(self, messages, model, **kwargs):
            raise ConnectionError("Down")

    config = {
        "models": {
            "default": {
                "primary": {"provider": "fail", "model": "m1"},
            },
        }
    }
    router = ModelRouter(config, {"fail": FailingProvider()})
    gateway = LLMGateway(router)

    with pytest.raises(RuntimeError, match="All providers failed"):
        await gateway.complete(messages=[{"role": "user", "content": "hi"}], model="default")


def test_router_unknown_model(mock_provider):
    config = {"models": {"default": {"primary": {"provider": "mock", "model": "m"}}}}
    router = ModelRouter(config, {"mock": mock_provider})

    with pytest.raises(ValueError, match="Unknown model"):
        router.resolve("nonexistent")
