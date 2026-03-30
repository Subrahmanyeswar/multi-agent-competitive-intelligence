import logging
from datetime import datetime
from agents.research_agent import ResearchAgentBuilder  # pyre-ignore[21]  # type: ignore
from pipelines.chunker import SemanticChunker  # pyre-ignore[21]  # type: ignore
from storage.vector_store import vector_store  # pyre-ignore[21]  # type: ignore
from config.settings import settings  # pyre-ignore[21]  # type: ignore

logger = logging.getLogger(__name__)

class IngestionPipeline:
    """
    Full pipeline: scrape → clean → chunk → embed → upsert.
    Runs for all competitors defined in config/competitors.yaml.
    """
    
    def __init__(self):
        self.researcher = ResearchAgentBuilder()
        self.chunker = SemanticChunker()
        from typing import Any
        self.stats: dict[str, Any] = {
            "companies_processed": 0,
            "articles_collected": 0,
            "chunks_upserted": 0,
            "errors": [],
        }
    
    def run_for_company(self, company: dict) -> dict:
        """Run full ingestion for a single competitor."""
        company_name = company["name"]
        logger.info(f"[Pipeline] Starting ingestion for: {company_name}")
        
        company_stats = {
            "company": company_name,
            "articles": 0,
            "chunks": 0,
            "status": "success",
        }
        
        try:
            # Step 1: Collect raw articles
            articles = self.researcher.collect_raw_data(company)
            company_stats["articles"] = len(articles)
            
            if not articles:
                logger.warning(f"No new articles found for {company_name}")
                company_stats["status"] = "no_data"
                return company_stats
            
            # Step 2: Chunk all articles
            all_chunks = []
            for article in articles:
                chunks = self.chunker.chunk_article(article)
                all_chunks.extend(chunks)
            
            logger.info(f"[Pipeline] {company_name}: {len(all_chunks)} chunks ready")
            
            # Step 3: Upsert to Qdrant
            logger.info(f"[Pipeline] {company_name}: {len(all_chunks)} chunks to upsert")
            if all_chunks:
                upserted = vector_store.upsert(all_chunks)
                company_stats["chunks"] = upserted
                self.stats["chunks_upserted"] += upserted
                logger.info(f"[Pipeline] {company_name}: upserted {upserted} chunks to Qdrant")
            else:
                logger.warning(f"[Pipeline] {company_name}: 0 chunks — articles may already be in DB but not Qdrant")
            
            self.stats["articles_collected"] += len(articles)
            self.stats["companies_processed"] += 1
            
        except Exception as e:
            logger.error(f"[Pipeline] Failed for {company_name}: {e}", exc_info=True)
            company_stats["status"] = f"error: {str(e)}"
            self.stats["errors"].append({"company": company_name, "error": str(e)})
        
        return company_stats
    
    def run_all(self) -> dict:
        """Run ingestion for all competitors in config."""
        competitors = settings.load_competitors()
        logger.info(f"[Pipeline] Starting full ingestion run for {len(competitors)} competitors")
        
        from typing import Any
        run_stats: dict[str, Any] = {
            "run_started": datetime.utcnow().isoformat(),
            "companies": [],
        }
        
        for company in competitors:
            result = self.run_for_company(company)
            run_stats["companies"].append(result)
        
        run_stats["run_completed"] = datetime.utcnow().isoformat()
        run_stats["totals"] = self.stats
        
        logger.info(f"[Pipeline] Run complete. Stats: {self.stats}")
        return run_stats
