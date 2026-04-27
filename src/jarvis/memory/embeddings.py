from src.jarvis.llm.gateway import LLMGateway


class EmbeddingService:
    def __init__(self, gateway: LLMGateway):
        self.gateway = gateway

    async def embed(self, text: str) -> list[float]:
        return await self.gateway.embed(text, model="embedding")
