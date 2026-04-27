import logging

from .providers.base import LLMProvider

logger = logging.getLogger(__name__)


class ModelRouter:
    """Resolves logical model names to providers and handles fallback."""

    def __init__(self, models_config: dict, providers: dict[str, LLMProvider]):
        self.config = models_config.get("models", {})
        self.providers = providers

    def resolve(self, logical_name: str) -> list[tuple[LLMProvider, str]]:
        """Return ordered list of (provider, model_name) to try."""
        model_cfg = self.config.get(logical_name)
        if not model_cfg:
            raise ValueError(f"Unknown model: {logical_name}")

        chain = []
        for key in ("primary", "fallback"):
            entry = model_cfg.get(key)
            if entry:
                provider = self.providers.get(entry["provider"])
                if provider:
                    chain.append((provider, entry["model"]))
        return chain
