from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict = field(default_factory=dict)


@dataclass
class LLMChunk:
    content: str
    done: bool = False


class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> LLMResponse | AsyncIterator[LLMChunk]:
        ...

    @abstractmethod
    async def embed(self, text: str, model: str) -> list[float]:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...
