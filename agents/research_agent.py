import logging
from tools.search_tool import SerperSearchTool
from tools.scraper_tool import FirecrawlScraperTool
from storage.database import save_article, article_exists
from config.settings import settings

logger = logging.getLogger(__name__)

def get_llm():
    from langchain_mistralai import ChatMistralAI
    return ChatMistralAI(
        model=settings.MISTRAL_MODEL,
        mistral_api_key=settings.MISTRAL_API_KEY,
        temperature=0.1,
    )

class ResearchAgentBuilder:
    """Builds a CrewAI Research Agent specialized per competitor."""
    
    def __init__(self):
        self.search_tool = SerperSearchTool()
        self.scraper_tool = FirecrawlScraperTool()
        self.llm = get_llm()
    
    def build(self, company: dict):
        from crewai import Agent
        return Agent(
            role=f"Market Intelligence Researcher for {company['name']}",
            goal=(
                f"Collect all significant news, product launches, partnerships, and strategic moves "
                f"by {company['name']} from the past 7 days. Return structured, factual data only."
            ),
            backstory=(
                f"You are a senior market intelligence analyst who has tracked {company['name']} "
                f"for 5 years. You specialize in identifying strategic signals from news data. "
                f"You never fabricate information — every claim must come from a real source."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
        )
    
    def collect_raw_data(self, company: dict) -> list[dict]:
        """
        Direct data collection (used by ingestion pipeline, not CrewAI task).
        Returns list of enriched article dicts.
        """
        logger.info(f"Starting data collection for: {company['name']}")
        
        # Step 1: Search for news
        articles = self.search_tool.search_competitor(company)
        
        # Step 2: Filter already-stored articles
        new_articles = [a for a in articles if not article_exists(a["url"])]
        logger.info(f"{len(new_articles)} new articles to scrape for {company['name']}")
        
        # Step 3: Scrape full content
        enriched = self.scraper_tool.scrape_batch(new_articles)
        
        # Step 4: Save to local DB
        for article in enriched:
            save_article(article)
        
        return enriched
