from functools import lru_cache

from config.settings import settings
from src.jarvis.llm.gateway import LLMGateway
from src.jarvis.llm.providers.ollama import OllamaProvider
from src.jarvis.llm.providers.openai import OpenAIProvider
from src.jarvis.llm.router import ModelRouter


@lru_cache
def get_llm_gateway() -> LLMGateway:
    providers: dict = {}

    providers["ollama"] = OllamaProvider(
        base_url=settings.ollama_base_url,
        timeout=settings.ollama_timeout,
    )

    if settings.openai_api_key:
        providers["openai"] = OpenAIProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    models_config = settings.load_models_config()
    router = ModelRouter(models_config, providers)
    return LLMGateway(router)
