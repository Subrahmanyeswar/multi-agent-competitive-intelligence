from crewai import Task
from agents.research_agent import ResearchAgentBuilder

def create_research_task(company: dict, agent) -> Task:
    return Task(
        description=(
            f"Collect the latest competitive intelligence for {company['name']}.\n\n"
            f"Search for news using these keywords: {', '.join(company.get('keywords', [company['name']]))}\n"
            f"Focus on these categories: {', '.join(company.get('categories', ['general']))}\n\n"
            f"For each article found:\n"
            f"1. Extract the headline and key facts\n"
            f"2. Identify which strategic category it belongs to (product/partnership/funding/hiring)\n"
            f"3. Assess if this represents a significant competitive move (high/medium/low)\n\n"
            f"Return a structured JSON list with fields: title, url, date, category, significance, key_facts"
        ),
        expected_output=(
            f"A JSON array of news items for {company['name']}. "
            f"Each item must have: title (str), url (str), date (str), "
            f"category (str), significance (high/medium/low), key_facts (list of str). "
            f"Minimum 3 items, maximum 15 items. No fabricated data."
        ),
        agent=agent,
    )
