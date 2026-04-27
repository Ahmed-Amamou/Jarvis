import logging
from typing import AsyncIterator

from .providers.base import LLMChunk, LLMProvider, LLMResponse
from .router import ModelRouter

logger = logging.getLogger(__name__)


class LLMGateway:
    """Unified LLM interface with automatic fallback."""

    def __init__(self, router: ModelRouter):
        self.router = router

    async def complete(
        self,
        messages: list[dict],
        model: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> LLMResponse | AsyncIterator[LLMChunk]:
        chain = self.router.resolve(model)
        last_error = None

        for provider, model_name in chain:
            try:
                logger.info(f"Trying {provider.__class__.__name__} with {model_name}")
                result = await provider.complete(
                    messages=messages,
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                )
                return result
            except Exception as e:
                logger.warning(f"{provider.__class__.__name__} failed: {e}")
                last_error = e

        raise RuntimeError(f"All providers failed. Last error: {last_error}")

    async def embed(self, text: str, model: str = "embedding") -> list[float]:
        chain = self.router.resolve(model)
        last_error = None

        for provider, model_name in chain:
            try:
                return await provider.embed(text, model_name)
            except Exception as e:
                logger.warning(f"Embedding failed with {provider.__class__.__name__}: {e}")
                last_error = e

        raise RuntimeError(f"All embedding providers failed. Last error: {last_error}")
