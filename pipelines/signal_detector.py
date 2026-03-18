import logging
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Any, cast, List, Dict, Set
from storage.database import load_db

logger = logging.getLogger(__name__)

class SignalDetector:
    """
    Detects weak signals across the full article corpus using:
    1. Signal Velocity — rate of change in mention frequency
    2. Geographic/Source Spread — diversity of sources mentioning a topic
    3. Sentiment Momentum — normalized sentiment score over time
    4. Convergence Score — topic appearing across multiple data types
    """
    
    STRATEGIC_KEYWORDS = {
        "acquisition": ["acqui", "merger", "buyout", "takeover"],
        "product_launch": ["launch", "release", "unveil", "announce", "introduce"],
        "market_expansion": ["expand", "enter", "new market", "global", "international"],
        "funding": ["raise", "funding", "series", "investment", "valuation"],
        "leadership": ["appoint", "hire", "ceo", "cto", "chief", "executive"],
        "partnership": ["partner", "collaborate", "alliance", "joint venture"],
        "regulatory": ["regulation", "compliance", "fine", "lawsuit", "antitrust"],
        "technology": ["patent", "ai", "model", "breakthrough", "research"],
    }
    
    def __init__(self, lookback_days: int = 7):
        self.lookback_days = lookback_days
        self.cutoff = datetime.utcnow() - timedelta(days=lookback_days)
    
    def load_recent_articles(self) -> list[dict]:
        all_articles = load_db()
        recent = []
        for a in all_articles:
            try:
                date_str = a.get("stored_at") or a.get("date", "")
                if date_str:
                    # Handle multiple date formats
                    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                        try:
                            article_date = datetime.strptime(date_str[:19], fmt[:len(date_str[:19])])
                            if article_date >= self.cutoff:
                                recent.append(a)
                            break
                        except ValueError:
                            continue
            except Exception:
                recent.append(a)  # include if date parsing fails
        return recent
    
    def detect_topic_velocity(self, articles: list[dict]) -> list[dict]:
        """
        For each strategic keyword category, count mentions in recent vs older articles.
        Velocity = recent_count / max(older_count, 1) — values > 1.5 indicate acceleration.
        """
        topic_counts = defaultdict(lambda: {"recent": 0, "older": 0, "companies": set()})
        
        all_articles = load_db()
        mid_cutoff = datetime.utcnow() - timedelta(days=self.lookback_days * 2)
        
        for article in all_articles:
            text = (
                article.get("title", "") + " " +
                article.get("snippet", "") + " " +
                article.get("full_content", "")[:500]
            ).lower()
            
            # Determine if recent or older
            date_str = article.get("stored_at", "")
            is_recent = True
            try:
                article_date = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
                is_recent = article_date >= self.cutoff
            except Exception:
                pass
            
            for topic, keywords in self.STRATEGIC_KEYWORDS.items():
                if any(kw in text for kw in keywords):
                    if is_recent:
                        topic_counts[topic]["recent"] += 1
                    else:
                        topic_counts[topic]["older"] += 1
                    topic_counts[topic]["companies"].add(str(article.get("company", "unknown")))
        
        signals = []
        for topic, counts in topic_counts.items():
            if counts["recent"] == 0:
                continue
            recent_count = int(counts["recent"])
            older_count = int(counts["older"])
            velocity = float(recent_count) / max(older_count, 1)
            spread = len(counts["companies"])
            
            # Convergence: topic appearing across multiple categories is stronger
            convergence = min(spread / max(len(self.STRATEGIC_KEYWORDS), 1) * 5, 1.0)
            
            # Normalize velocity to 0-1 scale (cap at 10x = max signal)
            velocity_normalized = min(velocity / 10.0, 1.0)
            spread_normalized = min(spread / 3.0, 1.0)  # 3 companies = max spread
            
            composite_score = round(
                (velocity_normalized * 0.5 +
                 spread_normalized * 0.3 +
                 counts["recent"] / max(counts["recent"] + counts["older"], 1) * 0.2),
                3
            )
            
            signals.append({
                "topic": topic,
                "velocity": round(velocity, 2),
                "source_spread": spread,
                "companies_involved": sorted(list(cast(Set, counts["companies"]))),
                "recent_mentions": counts["recent"],
                "composite_score": min(composite_score, 1.0),
                "signal_strength": (
                    "strong" if composite_score > 0.7
                    else "moderate" if composite_score > 0.4
                    else "weak"
                ),
            })
        
        signals.sort(key=lambda x: x["composite_score"], reverse=True)
        return signals
    
    def detect_company_momentum(self, company_name: str) -> dict:
        """
        Compute momentum for a specific company based on article frequency
        and sentiment trend over the past 7 days.
        """
        articles = [
            a for a in self.load_recent_articles()
            if a.get("company") == company_name
        ]
        
        if not articles:
            return {"company": company_name, "momentum": 0.0, "trend": "neutral", "article_count": 0}
        
        # Positive/negative keyword counts
        pos_words = ["launch", "growth", "partner", "raise", "award", "milestone", "expand", "win"]
        neg_words = ["layoff", "fine", "lawsuit", "breach", "delay", "miss", "decline", "fail"]
        
        pos_score = 0
        neg_score = 0
        
        for article in articles:
            text = (article.get("title", "") + " " + article.get("snippet", "")).lower()
            pos_score += sum(1 for w in pos_words if w in text)
            neg_score += sum(1 for w in neg_words if w in text)
        
        total = pos_score + neg_score
        if total == 0:
            momentum = 0.5
        else:
            momentum = pos_score / total
        
        return {
            "company": company_name,
            "momentum": round(momentum, 3),
            "trend": "positive" if momentum > 0.6 else "negative" if momentum < 0.4 else "neutral",
            "article_count": len(articles),
            "positive_signals": pos_score,
            "negative_signals": neg_score,
        }
    
    def run_full_detection(self, competitor_names: list[str]) -> dict:
        """Run all detection algorithms and return combined signal report."""
        logger.info("[SignalDetector] Running full weak signal detection")
        
        articles = self.load_recent_articles()
        topic_signals = self.detect_topic_velocity(articles)
        company_momentum = [self.detect_company_momentum(c) for c in competitor_names]
        
        return {
            "detection_date": datetime.utcnow().isoformat(),
            "articles_analyzed": len(articles),
            "topic_signals": topic_signals[:10],  # top 10 topics
            "company_momentum": company_momentum,
            "top_signal": topic_signals[0] if topic_signals else None,
        }
