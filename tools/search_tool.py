import requests
import logging
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings

logger = logging.getLogger(__name__)

class SerperSearchTool:
    """Searches Google News for competitor mentions using Serper API."""
    
    BASE_URL = "https://google.serper.dev/news"
    
    def __init__(self):
        self.api_key = settings.SERPER_API_KEY
        self.headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search(self, query: str, num_results: int = 10) -> list[dict]:
        payload = {
            "q": query,
            "num": num_results,
            "gl": "us",
            "hl": "en",
        }
        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            results = []
            for item in data.get("news", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": item.get("source", ""),
                    "date": item.get("date", datetime.utcnow().isoformat()),
                })
            logger.info(f"Serper: found {len(results)} results for '{query}'")
            return results
        except Exception as e:
            logger.error(f"Serper search failed for '{query}': {e}")
            return []
    
    def search_competitor(self, company: dict) -> list[dict]:
        all_results = []
        seen_urls = set()
        company_name = company["name"]
        keywords = company.get("keywords", [company["name"]])
        
        # Build exact match terms for strict filtering
        exact_terms = [k.lower() for k in keywords] + [company_name.lower()]
        
        for keyword in keywords:
            results = self.search(
                f'"{keyword}" news site:reuters.com OR site:bloomberg.com '
                f'OR site:economictimes.indiatimes.com OR site:livemint.com '
                f'OR site:businesstoday.in OR site:moneycontrol.com'
            )
            for r in results:
                if r["url"] in seen_urls:
                    continue
                
                title_lower = r.get("title", "").lower()
                snippet_lower = r.get("snippet", "").lower()
                combined = title_lower + " " + snippet_lower
                
                # Must mention at least one of our exact terms
                is_relevant = any(term in combined for term in exact_terms)
                
                if is_relevant:
                    seen_urls.add(r["url"])
                    r["company"] = company_name
                    all_results.append(r)
        
        logger.info(f"Relevant articles for {company_name}: {len(all_results)}")
        return all_results
