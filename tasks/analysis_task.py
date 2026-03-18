from crewai import Task

def create_analysis_task(company_name: str, agent, context_tasks: list = None) -> Task:
    return Task(
        description=(
            f"Perform a full competitive analysis of {company_name} using all collected data.\n\n"
            f"Your analysis must include:\n"
            f"1. SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)\n"
            f"2. Key developments this week (ranked by strategic significance)\n"
            f"3. Strategic themes emerging from recent activity\n"
            f"4. 30-day outlook for this competitor\n\n"
            f"Apply Porter's Five Forces thinking where relevant.\n"
            f"Identify any 'weak signals' — early indicators of strategic shifts.\n"
            f"All claims must be traceable to source data."
        ),
        expected_output=(
            f"A structured JSON analysis of {company_name} containing: "
            f"swot (object with 4 arrays), key_developments (array), "
            f"strategic_themes (array of strings), signal_velocity (float 0-1), "
            f"outlook (string paragraph). "
            f"Total response length 400-800 words of substantive insight."
        ),
        agent=agent,
        context=context_tasks or [],
    )
