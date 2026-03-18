import logging
import re
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class WeakSignalScorer:
    """
    Scores competitive signals using:
    - Signal Velocity: rate of change in mention frequency
    - Sentiment Momentum: positive/negative indicator from text
    - Strategic Weight: category-based importance multiplier
    """
    
    CATEGORY_WEIGHTS = {
        "product": 1.5,
        "funding": 1.8,
        "partnership": 1.4,
        "hiring": 1.2,
        "strategy": 1.6,
        "general": 1.0,
    }
    
    POSITIVE_SIGNALS = [
        "launch", "announce", "partnership", "acquire", "raise", "growth",
        "expand", "hire", "patent", "breakthrough", "record", "milestone",
    ]
    
    NEGATIVE_SIGNALS = [
        "layoff", "shutdown", "fine", "lawsuit", "delay", "miss",
        "decline", "breach", "controversy", "fail", "drop", "cut",
    ]
    
    def score_article(self, article: dict) -> dict:
        text = (article.get("title", "") + " " + article.get("snippet", "") + " " + article.get("full_content", "")).lower()
        
        # Sentiment momentum
        pos_count = sum(1 for s in self.POSITIVE_SIGNALS if s in text)
        neg_count = sum(1 for s in self.NEGATIVE_SIGNALS if s in text)
        sentiment = (pos_count - neg_count) / max(pos_count + neg_count, 1)
        
        # Category weight
        category = article.get("category", "general")
        weight = self.CATEGORY_WEIGHTS.get(category, 1.0)
        
        # Final score (0.0 to 1.0 scale)
        raw_score = (sentiment + 1) / 2  # normalize to [0, 1]
        final_score = min(raw_score * weight, 1.0)
        
        return {
            "sentiment_momentum": round(float(sentiment), 3),
            "category_weight": float(weight),
            "signal_score": round(float(final_score), 3),
            "signal_level": "high" if final_score > 0.65 else "medium" if final_score > 0.35 else "low",
        }
    
    def score_company_articles(self, articles: list[dict]) -> list[dict]:
        """Score all articles for a company and attach scores."""
        scored = []
        for article in articles:
            scores = self.score_article(article)
            article.update(scores)
            scored.append(article)
        
        # Sort by signal score descending
        scored.sort(key=lambda x: x.get("signal_score", 0), reverse=True)
        return scored
    
    def compute_velocity(self, articles: list[dict]) -> float:
        """
        Signal Velocity = number of high-signal articles in last 7 days
        divided by baseline (average over prior periods).
        """
        if not articles:
            return 0.0
        high_signal = [a for a in articles if a.get("signal_level") == "high"]
        velocity = float(len(high_signal)) / max(len(articles), 1)
        return round(velocity, 3)
