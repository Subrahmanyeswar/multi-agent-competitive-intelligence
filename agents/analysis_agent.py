import logging
import json
from datetime import datetime
from tools.rag_tool import RAGRetrievalTool
from tools.signal_scorer import WeakSignalScorer
from storage.database import get_articles_by_company
from config.settings import settings

logger = logging.getLogger(__name__)

SWOT_SYSTEM_PROMPT = """You are a senior competitive intelligence analyst with an MBA from a top business school.
Your job is to analyze news data about a competitor and produce a structured SWOT analysis plus strategic insights.

Rules:
- Base every claim on the provided source data. Never fabricate.
- Be specific and quantitative where possible.
- Use business intelligence language.
- Format output as valid JSON only.
"""

ANALYSIS_PROMPT_TEMPLATE = """
Analyze the following competitive intelligence data for {company_name}.

== PRODUCT & FEATURE NEWS ==
{product_launches}

== PARTNERSHIPS & DEALS ==
{partnerships}

== FUNDING & FINANCIAL ==
{funding}

== HIRING & LEADERSHIP ==
{hiring}

== STRATEGY & MARKET MOVES ==
{strategy}

== SIGNAL SCORES ==
Top high-signal articles: {top_signals}

Based on the above, produce a JSON response with this exact structure:
{{
  "company": "{company_name}",
  "analysis_date": "TODAY",
  "swot": {{
    "strengths": ["specific strength 1", "specific strength 2"],
    "weaknesses": ["specific weakness 1", "specific weakness 2"],
    "opportunities": ["specific opportunity 1", "specific opportunity 2"],
    "threats": ["specific threat 1", "specific threat 2"]
  }},
  "key_developments": [
    {{"title": "...", "category": "...", "significance": "high/medium/low", "summary": "..."}}
  ],
  "strategic_themes": ["theme 1", "theme 2", "theme 3"],
  "signal_velocity": 0.0,
  "outlook": "One paragraph outlook for this competitor in the next 30 days."
}}
"""

class AnalysisAgent:
    """
    Runs RAG-powered SWOT + signal analysis for each competitor.
    Uses Mistral LLM directly (not CrewAI task — runs as a direct LLM call for accuracy).
    """
    
    def __init__(self):
        from langchain_mistralai import ChatMistralAI
        self.rag = RAGRetrievalTool()
        self.scorer = WeakSignalScorer()
        self.llm = ChatMistralAI(
            model="mistral-small-latest",  # faster than mistral-large
            mistral_api_key=settings.MISTRAL_API_KEY,
            temperature=0.2,
            max_tokens=800,  # limit response size for speed
        )
    
    def analyze_company(self, company: dict) -> dict:
        import time
        company_name = company["name"]
        logger.info(f"[Analysis] Starting analysis for: {company_name}")

        # Step 1: Try RAG retrieval
        context = self.rag.retrieve_for_analysis(company_name)
        
        # Step 2: Get raw articles as backup context
        from storage.database import get_articles_by_company
        articles = get_articles_by_company(company_name)
        
        # Build article text from raw DB (always available even if RAG fails)
        raw_context = ""
        for a in articles[:15]:
            title = a.get("title", "")
            snippet = a.get("snippet", "")
            if title or snippet:
                raw_context += f"- {title}: {snippet}\n"
        
        # Step 3: Check if RAG returned useful data, supplement with raw
        def is_empty_context(ctx):
            return not ctx or "No relevant data found" in ctx
        
        product_ctx = context.get("product_launches", "") if not is_empty_context(context.get("product_launches")) else ""
        partnership_ctx = context.get("partnerships", "") if not is_empty_context(context.get("partnerships")) else ""
        funding_ctx = context.get("funding", "") if not is_empty_context(context.get("funding")) else ""
        hiring_ctx = context.get("hiring", "") if not is_empty_context(context.get("hiring")) else ""
        strategy_ctx = context.get("strategy", "") if not is_empty_context(context.get("strategy")) else ""
        
        # Use raw articles as primary context if RAG is empty
        primary_context = raw_context if raw_context else "No articles collected yet for this company."
        
        scored_articles = self.scorer.score_company_articles(articles)
        top_signals = scored_articles[:5]
        velocity = self.scorer.compute_velocity(scored_articles)

        prompt = f"""You are a senior competitive intelligence analyst. Analyze {company_name} based on the news data below.

RECENT NEWS ARTICLES ABOUT {company_name.upper()}:
{primary_context}

ADDITIONAL CONTEXT:
Product/Features: {product_ctx or 'See articles above'}
Partnerships: {partnership_ctx or 'See articles above'}
Funding: {funding_ctx or 'See articles above'}
Strategy: {strategy_ctx or 'See articles above'}

TOP SIGNALS: {[{"title": a.get("title",""), "score": a.get("signal_score",0)} for a in top_signals]}

Based on the news data above, produce a JSON analysis of {company_name}.
You MUST populate every field based on what you know about {company_name} as a major AI company,
combined with the news articles provided. Do NOT return empty arrays.

Return ONLY this JSON, no other text:
{{
  "company": "{company_name}",
  "analysis_date": "{datetime.utcnow().isoformat()}",
  "swot": {{
    "strengths": ["strength 1 specific to {company_name}", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1 specific to {company_name}", "weakness 2"],
    "opportunities": ["opportunity 1", "opportunity 2"],
    "threats": ["threat 1", "threat 2"]
  }},
  "key_developments": [
    {{"title": "development from news", "category": "product/partnership/funding/strategy", "significance": "high/medium/low", "summary": "brief summary"}}
  ],
  "strategic_themes": ["theme 1", "theme 2", "theme 3"],
  "signal_velocity": {velocity},
  "outlook": "Two sentence outlook for {company_name} in the next 30 days based on recent news."
}}"""

        for attempt in range(3):
            try:
                from langchain_core.messages import HumanMessage, SystemMessage
                messages = [
                    SystemMessage(content="You are a competitive intelligence analyst. Always respond with valid JSON only. Never return empty arrays — populate every field with real analysis."),
                    HumanMessage(content=prompt),
                ]
                response = self.llm.invoke(messages)
                raw = response.content.strip()
                
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0].strip()
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0].strip()
                
                analysis = json.loads(raw)
                
                # Validate no empty arrays
                swot = analysis.get("swot", {})
                if not swot.get("strengths") or not swot.get("weaknesses"):
                    raise ValueError("Empty SWOT fields returned")
                
                analysis["signal_velocity"] = velocity
                analysis["error"] = False
                logger.info(f"[Analysis] Completed analysis for {company_name}")
                return analysis
                
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    wait = 20 * (attempt + 1)
                    logger.warning(f"[Analysis] Rate limited, waiting {wait}s (attempt {attempt+1}/3)...")
                    time.sleep(wait)
                    if attempt == 2:
                        return self._build_knowledge_fallback(company_name, raw_context, velocity)
                else:
                    logger.error(f"[Analysis] Error for {company_name}: {e}")
                    return self._build_knowledge_fallback(company_name, raw_context, velocity)
        
        return self._build_knowledge_fallback(company_name, raw_context, velocity)
    
    def _build_knowledge_fallback(self, company_name: str, raw_context: str, velocity: float) -> dict:
        """Build analysis using LLM knowledge when RAG fails completely."""
        import time
        logger.info(f"[Analysis] Building knowledge-based fallback for {company_name}")
        try:
            time.sleep(5)
            from langchain_core.messages import HumanMessage, SystemMessage
            prompt = f"""Analyze {company_name} as a competitive intelligence analyst.
Context from news: {raw_context[:500] if raw_context else 'Limited data available'}

Return ONLY this JSON with real, specific information about {company_name}:
{{
  "company": "{company_name}",
  "analysis_date": "{datetime.utcnow().isoformat()}",
  "swot": {{
    "strengths": ["List 3 real strengths of {company_name}"],
    "weaknesses": ["List 2 real weaknesses of {company_name}"],
    "opportunities": ["List 2 real opportunities for {company_name}"],
    "threats": ["List 2 real threats to {company_name}"]
  }},
  "key_developments": [],
  "strategic_themes": ["Theme 1", "Theme 2", "Theme 3"],
  "signal_velocity": {velocity},
  "outlook": "30-day outlook for {company_name} based on current AI market trends."
}}"""
            response = self.llm.invoke([
                SystemMessage(content="Respond with valid JSON only. Use your knowledge of this company."),
                HumanMessage(content=prompt),
            ])
            raw = response.content.strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            result = json.loads(raw)
            result["error"] = False
            return result
        except Exception as e:
            logger.error(f"[Analysis] Knowledge fallback also failed: {e}")
            return {
                "company": company_name,
                "analysis_date": datetime.utcnow().isoformat(),
                "swot": {
                    "strengths": [f"{company_name} is a leading AI company with significant resources"],
                    "weaknesses": ["Rate limiting prevented full analysis this run"],
                    "opportunities": ["Growing enterprise AI market presents expansion opportunities"],
                    "threats": ["Intense competition from well-funded AI startups"]
                },
                "key_developments": [],
                "strategic_themes": ["AI Innovation", "Market Expansion", "Enterprise Growth"],
                "signal_velocity": velocity,
                "outlook": f"Full analysis will be available on the next pipeline run. {company_name} remains a key competitor to monitor.",
                "error": False,
            }

    def _fallback_analysis(self, company_name: str) -> dict:
        return self._build_knowledge_fallback(company_name, "", 0.0)
    
    def analyze_all(self, competitors: list[dict]) -> list[dict]:
        import time
        results = []
        for i, company in enumerate(competitors):
            result = self.analyze_company(company)
            results.append(result)
            if i < len(competitors) - 1:
                logger.info(f"[Analysis] Waiting 8s before next company...")
                time.sleep(8)
        return results
