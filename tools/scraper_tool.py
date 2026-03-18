import logging
import time
from firecrawl import FirecrawlApp
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings

logger = logging.getLogger(__name__)

class FirecrawlScraperTool:
    """Scrapes full article content from URLs using Firecrawl."""
    
    def __init__(self):
        self.app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY)
        self.rate_limit_delay = 1.5  # seconds between requests
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=3, max=15))
    def scrape_url(self, url: str) -> dict:
        try:
            time.sleep(self.rate_limit_delay)
            result = self.app.scrape_url(url, params={"formats": ["markdown"]})
            content = ""
            if hasattr(result, "markdown"):
                content = result.markdown or ""
            elif isinstance(result, dict):
                content = result.get("markdown", result.get("content", ""))
            
            # Clean boilerplate
            content = self._clean_content(content)
            logger.info(f"Scraped {len(content)} chars from {url}")
            return {"url": url, "content": content, "success": True}
        except Exception as e:
            logger.warning(f"Firecrawl failed for {url}: {e}")
            return {"url": url, "content": "", "success": False, "error": str(e)}
    
    def _clean_content(self, text: str) -> str:
        """Remove common boilerplate patterns."""
        lines = text.split("\n")
        cleaned = []
        skip_patterns = [
            "cookie", "subscribe", "newsletter", "advertisement",
            "follow us", "share this", "related articles", "also read"
        ]
        for line in lines:
            line = line.strip()
            if len(line) < 20:
                continue
            if any(p in line.lower() for p in skip_patterns):
                continue
            cleaned.append(line)
        return "\n".join(cleaned)
    
    def scrape_batch(self, articles: list[dict]) -> list[dict]:
        """Scrape a list of articles, adding full content to each."""
        enriched = []
        for article in articles:
            url = article.get("url", "")
            if not url:
                continue
            scraped = self.scrape_url(url)
            article["full_content"] = scraped["content"]
            article["scrape_success"] = scraped["success"]
            if scraped["content"]:
                enriched.append(article)
        logger.info(f"Successfully scraped {len(enriched)}/{len(articles)} articles")
        return enriched
