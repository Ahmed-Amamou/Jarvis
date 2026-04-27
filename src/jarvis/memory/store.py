import logging
from dataclasses import dataclass
from uuid import uuid4

from pinecone import Pinecone

from .embeddings import EmbeddingService

logger = logging.getLogger(__name__)


@dataclass
class MemoryResult:
    id: str
    text: str
    score: float
    metadata: dict


class MemoryStore:
    def __init__(self, api_key: str, index_name: str, embedding_service: EmbeddingService):
        self.embedding = embedding_service
        self._pc = Pinecone(api_key=api_key) if api_key else None
        self._index = self._pc.Index(index_name) if self._pc else None

    async def store(
        self,
        content: str,
        metadata: dict | None = None,
        namespace: str = "conversations",
    ) -> str | None:
        if not self._index:
            logger.debug("Pinecone not configured, skipping store")
            return None

        vector = await self.embedding.embed(content)
        vec_id = str(uuid4())
        meta = {"text": content, **(metadata or {})}
        self._index.upsert(vectors=[(vec_id, vector, meta)], namespace=namespace)
        logger.info(f"Stored memory {vec_id} in namespace {namespace}")
        return vec_id

    async def search(
        self,
        query: str,
        top_k: int = 5,
        namespace: str = "conversations",
        filter: dict | None = None,
    ) -> list[MemoryResult]:
        if not self._index:
            return []

        vector = await self.embedding.embed(query)
        results = self._index.query(
            vector=vector,
            top_k=top_k,
            filter=filter,
            include_metadata=True,
            namespace=namespace,
        )

        return [
            MemoryResult(
                id=match.id,
                text=match.metadata.get("text", ""),
                score=match.score,
                metadata=match.metadata,
            )
            for match in results.matches
        ]

    async def forget(self, ids: list[str], namespace: str = "conversations") -> None:
        if self._index:
            self._index.delete(ids=ids, namespace=namespace)
