from fastapi import APIRouter, Depends

from src.jarvis.api.deps import get_llm_gateway
from src.jarvis.api.schemas import HealthResponse
from src.jarvis.llm.gateway import LLMGateway

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(gateway: LLMGateway = Depends(get_llm_gateway)):
    ollama_ok = False
    chain = gateway.router.resolve("default")
    if chain:
        provider = chain[0][0]
        ollama_ok = await provider.health_check()

    return HealthResponse(
        status="ok" if ollama_ok else "degraded",
        ollama=ollama_ok,
    )
