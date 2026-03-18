import re
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class SemanticChunker:
    """
    Splits article text into semantic chunks respecting sentence boundaries.
    Uses paragraph-first, then sentence-level splitting.
    """
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.overlap = settings.CHUNK_OVERLAP
    
    def chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping semantic chunks."""
        size = int(self.chunk_size or 500)
        overlap = int(self.overlap or 50)
        
        if not text or len(text.strip()) < 50:
            return []
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # If adding this paragraph exceeds chunk_size, flush current
            if len(current_chunk) + len(para) > size and current_chunk:
                chunks.append(current_chunk.strip())
                # Keep overlap: last N chars of current chunk
                overlap_text = str(current_chunk)[-overlap:] if overlap > 0 else ""
                current_chunk = overlap_text + " " + para
            else:
                current_chunk += " " + para
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Filter out very short chunks
        final_chunks: list[str] = [str(c) for c in chunks if len(str(c)) > 80]
        logger.debug(f"Chunked text into {len(final_chunks)} chunks")
        return final_chunks
    
    def chunk_article(self, article: dict) -> list[dict]:
        """Convert one article dict into a list of chunk dicts with metadata."""
        content = article.get("full_content", "") or article.get("snippet", "")
        title = article.get("title", "")
        
        # Prepend title to first chunk for context
        full_text = f"{title}\n\n{content}" if content else title
        
        raw_chunks = self.chunk_text(full_text)
        if not raw_chunks:
            return []
        
        enriched_chunks = []
        for i, chunk_text in enumerate(raw_chunks):
            enriched_chunks.append({
                "text": chunk_text,
                "company": article.get("company", ""),
                "source_url": article.get("url", ""),
                "title": title,
                "date": article.get("date", ""),
                "category": article.get("category", "general"),
                "chunk_index": i,
            })
        
        return enriched_chunks
