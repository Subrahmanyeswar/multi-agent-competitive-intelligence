import logging
from config.settings import settings

logger = logging.getLogger(__name__)

def build_manager_agent():
    """
    The Manager Agent orchestrates the full crew.
    In CrewAI hierarchical mode, this agent plans and delegates tasks.
    """
    from crewai import Agent
    from langchain_mistralai import ChatMistralAI
    llm = ChatMistralAI(
        model=settings.MISTRAL_MODEL,
        mistral_api_key=settings.MISTRAL_API_KEY,
        temperature=0.1,
    )
    
    return Agent(
        role="Chief Intelligence Officer",
        goal=(
            "Orchestrate a team of specialized agents to produce a complete, accurate, "
            "and actionable weekly competitive intelligence report. "
            "Ensure all data is collected, analyzed, and synthesized without gaps."
        ),
        backstory=(
            "You are the CIO of a competitive intelligence firm managing a team of analysts. "
            "You assign work, validate outputs, and ensure the final report meets "
            "executive quality standards. You never accept incomplete or fabricated data."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=True,
    )


def build_analysis_crewai_agent():
    """CrewAI-compatible Analysis Agent for crew assembly."""
    from crewai import Agent
    from langchain_mistralai import ChatMistralAI
    llm = ChatMistralAI(
        model=settings.MISTRAL_MODEL,
        mistral_api_key=settings.MISTRAL_API_KEY,
        temperature=0.2,
    )
    return Agent(
        role="Strategic Analysis Specialist",
        goal=(
            "Analyze competitive intelligence data using SWOT frameworks, "
            "Porter's Five Forces, and weak signal detection. "
            "Produce structured, evidence-based insights."
        ),
        backstory=(
            "You are a strategy consultant with 10 years of competitive intelligence experience. "
            "You transform raw news data into actionable strategic insights. "
            "You apply rigorous analytical frameworks to every analysis."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def build_synthesizer_crewai_agent():
    """CrewAI-compatible Synthesizer Agent for crew assembly."""
    from crewai import Agent
    from langchain_mistralai import ChatMistralAI
    llm = ChatMistralAI(
        model=settings.MISTRAL_MODEL,
        mistral_api_key=settings.MISTRAL_API_KEY,
        temperature=0.3,
    )
    return Agent(
        role="Executive Report Writer",
        goal=(
            "Write a polished, professional, well-structured weekly competitive intelligence "
            "report that a CEO can read in under 5 minutes and take action from."
        ),
        backstory=(
            "You are a former McKinsey consultant turned intelligence writer. "
            "You specialize in distilling complex competitive data into clear, "
            "executive-ready reports with precise language and no filler."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )
