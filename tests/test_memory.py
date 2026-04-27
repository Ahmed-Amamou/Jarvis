from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.jarvis.memory.embeddings import EmbeddingService
from src.jarvis.memory.store import MemoryStore


@pytest.mark.asyncio
async def test_memory_store_no_pinecone(mock_gateway):
    """When Pinecone is not configured, store/search should gracefully no-op."""
    embedding_svc = EmbeddingService(mock_gateway)
    store = MemoryStore(api_key="", index_name="test", embedding_service=embedding_svc)

    result = await store.store("test content")
    assert result is None

    results = await store.search("test query")
    assert results == []


@pytest.mark.asyncio
async def test_embedding_service(mock_gateway):
    svc = EmbeddingService(mock_gateway)
    vector = await svc.embed("hello world")
    assert isinstance(vector, list)
    assert len(vector) == 384
