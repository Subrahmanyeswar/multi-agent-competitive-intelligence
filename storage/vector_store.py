from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
    PayloadSchemaType
)
from sentence_transformers import SentenceTransformer
from config.settings import settings
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.client = None
        self.encoder = None
        self.collection = settings.COLLECTION_NAME

    def _lazy_init(self):
        if self.client is None:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
            self.encoder = SentenceTransformer(settings.EMBEDDING_MODEL)
            self._ensure_collection()

    def _ensure_collection(self):
        existing = [c.name for c in self.client.get_collections().collections]
        if self.collection not in existing:
            # Create collection with unnamed vectors (size 384 for all-MiniLM-L6-v2)
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {self.collection}")
            
            # Create payload index on "company" field for filtering
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name="company",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            logger.info("Created payload index on 'company' field")
        else:
            # Collection exists — ensure index exists too
            try:
                self.client.create_payload_index(
                    collection_name=self.collection,
                    field_name="company",
                    field_schema=PayloadSchemaType.KEYWORD,
                )
                logger.info("Ensured payload index on 'company' field")
            except Exception:
                pass  # Index already exists, that's fine

    def upsert(self, chunks: list[dict]) -> int:
        self._lazy_init()
        points = []
        for chunk in chunks:
            # Encode as plain list (unnamed vector)
            vector = self.encoder.encode(chunk["text"]).tolist()
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,  # plain list, not named dict
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
        self.client.upsert(collection_name=self.collection, points=points)
        logger.info(f"Upserted {len(points)} chunks to Qdrant")
        return len(points)

    def search(self, query: str, company: str = None, top_k: int = None) -> list[dict]:
        self._lazy_init()
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        top_k = top_k or settings.TOP_K_RETRIEVAL
        
        # Encode as plain list (unnamed vector)
        vector = self.encoder.encode(query).tolist()
        
        query_filter = None
        if company:
            query_filter = Filter(
                must=[FieldCondition(key="company", match=MatchValue(value=company))]
            )
        
        results = self.client.search(
            collection_name=self.collection,
            query_vector=vector,  # plain list
            query_filter=query_filter,
            limit=top_k,
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

vector_store = VectorStore()
