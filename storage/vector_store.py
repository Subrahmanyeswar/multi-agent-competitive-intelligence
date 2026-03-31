# pyre-ignore-all-errors
from __future__ import annotations
from typing import Optional, Any

from qdrant_client import QdrantClient  # type: ignore
from qdrant_client.models import (  # type: ignore
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
    PayloadSchemaType
)
from sentence_transformers import SentenceTransformer  # type: ignore
from config.settings import settings  # pyre-ignore[21]  # type: ignore
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self) -> None:
        self.client: Optional[QdrantClient] = None
        self.encoder: Optional[SentenceTransformer] = None
        self.collection: str = settings.COLLECTION_NAME

    def _lazy_init(self) -> None:
        if self.client is None:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
            self.encoder = SentenceTransformer(settings.EMBEDDING_MODEL)
            self._ensure_collection()

    def _ensure_collection(self) -> None:
        client = self.client
        if client is None:
            return
        existing = [c.name for c in client.get_collections().collections]
        if self.collection not in existing:
            client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {self.collection}")
            client.create_payload_index(
                collection_name=self.collection,
                field_name="company",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            logger.info("Created payload index on 'company' field")
        else:
            try:
                client.create_payload_index(
                    collection_name=self.collection,
                    field_name="company",
                    field_schema=PayloadSchemaType.KEYWORD,
                )
                logger.info("Ensured payload index on 'company' field")
            except Exception:
                pass

    def upsert(self, chunks: list[dict[str, Any]]) -> int:
        self._lazy_init()
        client = self.client
        encoder = self.encoder
        if client is None or encoder is None:
            return 0
        points = []
        for chunk in chunks:
            vector = encoder.encode(chunk["text"]).tolist()  # pyre-ignore
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": chunk["text"],
                    "company": chunk.get("company", ""),
                    "source_url": chunk.get("source_url", ""),
                    "title": chunk.get("title", ""),
                    "date": chunk.get("date", datetime.utcnow().isoformat()),
                    "category": chunk.get("category", "general"),
                    "chunk_index": chunk.get("chunk_index", 0),
                }
            ))
        client.upsert(collection_name=self.collection, points=points)  # pyre-ignore
        logger.info(f"Upserted {len(points)} chunks to Qdrant")
        return len(points)

    def search(self, query: str, company: Optional[str] = None, top_k: Optional[int] = None) -> list[dict[str, Any]]:
        self._lazy_init()
        client = self.client
        encoder = self.encoder
        if client is None or encoder is None:
            return []
        resolved_top_k: int = top_k if top_k is not None else int(settings.TOP_K_RETRIEVAL)
        vector = encoder.encode(query).tolist()  # pyre-ignore
        
        query_filter = None
        if company:
            query_filter = Filter(
                must=[FieldCondition(key="company", match=MatchValue(value=company))]
            )
        
        results = client.search(  # pyre-ignore
            collection_name=self.collection,
            query_vector=vector,
            query_filter=query_filter,
            limit=resolved_top_k,
            with_payload=True,
        )
        return [
            {
                "text": r.payload["text"],
                "score": r.score,
                "company": r.payload.get("company"),
                "source_url": r.payload.get("source_url"),
                "title": r.payload.get("title"),
                "date": r.payload.get("date"),
            }
            for r in results
        ]

    def backfill_from_articles_db(self) -> int:
        """
        Embed and upsert all articles from articles.json that are
        not yet in Qdrant. Run this once to fix the empty vector store.
        """
        import json
        from pathlib import Path
        from pipelines.chunker import SemanticChunker  # pyre-ignore[21]  # type: ignore

        self._lazy_init()
        articles_path = Path(__file__).parent / "articles.json"

        if not articles_path.exists():
            logger.info("[Backfill] No articles.json found")
            return 0

        with open(articles_path, encoding="utf-8-sig") as f:
            content = f.read().strip()
            if not content:
                logger.info("[Backfill] articles.json is empty")
                return 0
            articles: list[dict[str, Any]] = json.loads(content)

        logger.info(f"[Backfill] Found {len(articles)} articles in DB")

        chunker = SemanticChunker()
        all_chunks: list[dict[str, Any]] = []

        for article in articles:
            chunks = chunker.chunk_article(article)
            all_chunks.extend(chunks)

        if not all_chunks:
            logger.info("[Backfill] No chunks generated")
            return 0

        logger.info(f"[Backfill] Generated {len(all_chunks)} chunks, upserting...")

        batch_size: int = 50
        total_upserted: int = 0
        for i in range(0, len(all_chunks), batch_size):
            batch: list[dict[str, Any]] = list(all_chunks[i:i + batch_size])  # pyre-ignore
            try:
                upserted: int = self.upsert(batch)
                total_upserted = int(total_upserted) + int(upserted)  # pyre-ignore
                logger.info(f"[Backfill] Batch {i // batch_size + 1}: upserted {upserted} chunks")
            except Exception as e:
                logger.error(f"[Backfill] Batch failed: {e}")

        logger.info(f"[Backfill] Complete — {total_upserted} total chunks in Qdrant")
        return int(total_upserted)  # pyre-ignore


vector_store = VectorStore()
