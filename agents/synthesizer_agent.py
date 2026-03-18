import json
import logging
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)

SYNTHESIZER_SYSTEM_PROMPT = """You are the Chief Intelligence Officer at a world-class competitive intelligence firm.
Your job is to synthesize analyses from multiple competitor research reports into a single, 
executive-grade weekly competitive landscape report.

Standards:
- Write in clear, professional business English.
- Be specific — name products, dollar amounts, dates where available.
- Every key claim must reference which company it applies to.
- Structure the report for a C-suite executive audience.
- Do not repeat the same information across sections.
- Output must be valid JSON only.
"""

SYNTHESIZER_PROMPT_TEMPLATE = """
You have received competitive analyses for {num_companies} companies this week:
{companies_list}

Here are the full analyses:

{all_analyses}

Today's date: {today}

Synthesize all of the above into a single weekly competitive intelligence report.
Return a JSON object with exactly this structure:

{{
  "report_title": "Weekly Competitive Intelligence Report — {today}",
  "executive_summary": "3-4 sentence paragraph covering the most critical developments across all companies this week.",
  "key_developments": [
    {{
      "company": "...",
      "development": "...",
      "significance": "high/medium/low",
      "strategic_implication": "..."
    }}
  ],
  "competitive_comparison": {{
    "most_active_company": "...",
    "most_active_reason": "...",
    "biggest_threat": "...",
    "biggest_opportunity": "..."
  }},
  "swot_summary": [
    {{
      "company": "...",
      "top_strength": "...",
      "top_threat": "..."
    }}
  ],
  "weak_signals": [
    {{
      "signal": "Description of the weak signal detected",
      "company": "...",
      "velocity_score": 0.0,
      "recommended_action": "What your organization should do in response"
    }}
  ],
  "outlook_30_days": "One paragraph covering expected competitive moves and market shifts in the next 30 days.",
  "strategic_recommendations": [
    {{
      "priority": "IMMEDIATE/HIGH/MEDIUM/MONITOR",
      "title": "Short action title",
      "action": "Specific concrete action to take",
      "target_competitor": "Which competitor this counters"
    }}
  ],
  "data_sources_count": 0,
  "companies_analyzed": []
}}
"""

class SynthesizerAgent:
    """
    Takes a list of per-company analysis dicts and produces
    the final unified weekly report as a structured dict.
    """
    
    def __init__(self):
        from langchain_mistralai import ChatMistralAI
        self.llm = ChatMistralAI(
            model="mistral-small-latest",
            mistral_api_key=settings.MISTRAL_API_KEY,
            temperature=0.3,
            max_tokens=1200,
        )
    
    def synthesize(self, analyses: list[dict]) -> dict:
        if not analyses:
            raise ValueError("No analyses provided to synthesizer")
        
        today = datetime.utcnow().strftime("%B %d, %Y")
        companies_list = "\n".join(f"- {a.get('company', 'Unknown')}" for a in analyses)
        
        # Format all analyses as readable JSON blocks
        all_analyses_text = ""
        for analysis in analyses:
            company = analysis.get("company", "Unknown")
            all_analyses_text += f"\n\n=== {company} ===\n"
            all_analyses_text += json.dumps(analysis, indent=2)
        
        prompt = SYNTHESIZER_PROMPT_TEMPLATE.format(
            num_companies=len(analyses),
            companies_list=companies_list,
            all_analyses=all_analyses_text,
            today=today,
        )
        
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content=SYNTHESIZER_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        
        logger.info(f"[Synthesizer] Running synthesis for {len(analyses)} companies")
        
        import time
        logger.info("[Synthesizer] Waiting 5s before LLM call (rate limit)...")
        time.sleep(5)
        
        for attempt in range(3):
            try:
                response = self.llm.invoke(messages)
                break
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    wait = 30 * (attempt + 1)
                    logger.warning(f"[Synthesizer] Rate limited, waiting {wait}s (attempt {attempt+1}/3)...")
                    time.sleep(wait)
                    if attempt == 2:
                        return self._fallback_report(analyses, today)
                else:
                    raise
        
        try:
            raw = response.content.strip()
            
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            
            report_data = json.loads(raw)
            
            # Enrich with metadata
            report_data["generated_at"] = datetime.utcnow().isoformat()
            report_data["companies_analyzed"] = [a.get("company") for a in analyses]
            report_data["data_sources_count"] = sum(
                len(a.get("key_developments", [])) for a in analyses
            )
            
            logger.info("[Synthesizer] Report synthesis complete")
            return report_data
            
        except json.JSONDecodeError as e:
            logger.error(f"[Synthesizer] JSON parse error: {e}")
            return self._fallback_report(analyses, today)
        except Exception as e:
            logger.error(f"[Synthesizer] LLM error: {e}", exc_info=True)
            return self._fallback_report(analyses, today)
    
    def _fallback_report(self, analyses: list[dict], today: str) -> dict:
        return {
            "report_title": f"Weekly Competitive Intelligence Report — {today}",
            "executive_summary": "Report generation encountered an error. Raw analysis data is preserved below.",
            "key_developments": [],
            "competitive_comparison": {},
            "swot_summary": [{"company": a.get("company"), "top_strength": "", "top_threat": ""} for a in analyses],
            "weak_signals": [],
            "outlook_30_days": "Outlook unavailable.",
            "generated_at": datetime.utcnow().isoformat(),
            "companies_analyzed": [a.get("company") for a in analyses],
            "data_sources_count": 0,
            "error": True,
        }
