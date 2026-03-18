import logging
from storage.vector_store import vector_store
from config.settings import settings

logger = logging.getLogger(__name__)

class RAGRetrievalTool:
    """
    Retrieves semantically relevant chunks from Qdrant for a given query and company.
    Formats them as a clean context block for the LLM.
    """
    
    def retrieve(self, query: str, company: str = None, top_k: int = None) -> str:
        results = vector_store.search(query=query, company=company, top_k=top_k)
        
        if not results:
            return f"No relevant data found for query: '{query}'"
        
        context_blocks = []
        for i, r in enumerate(results, 1):
            block = (
                f"[Source {i}] {r.get('title', 'Untitled')}\n"
                f"Company: {r.get('company', 'Unknown')} | "
                f"Date: {r.get('date', 'N/A')} | "
                f"URL: {r.get('source_url', 'N/A')}\n"
                f"Relevance score: {r.get('score', 0):.3f}\n"
                f"Content: {r['text']}\n"
            )
            context_blocks.append(block)
        
        return "\n---\n".join(context_blocks)
    
    def retrieve_for_analysis(self, company: str) -> dict:
        """
        Run multiple targeted queries for a company and return organized context.
        Covers product, partnership, funding, hiring, and strategic moves.
        """
        queries = {
            "product_launches": f"{company} new product launch feature release announcement",
            "partnerships": f"{company} partnership collaboration deal agreement",
            "funding": f"{company} funding investment valuation round",
            "hiring": f"{company} hiring executive appointment leadership",
            "strategy": f"{company} strategy market expansion competitive move",
        }
        
        context = {}
        for category, query in queries.items():
            context[category] = self.retrieve(query=query, company=company, top_k=5)
            logger.debug(f"Retrieved {category} context for {company}")
        
        return context
