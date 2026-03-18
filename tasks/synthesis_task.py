from crewai import Task

def create_synthesis_task(companies: list[str], agent, context_tasks: list = None) -> Task:
    companies_str = ", ".join(companies)
    return Task(
        description=(
            f"Synthesize all competitive analyses for {companies_str} into a single "
            f"executive-grade weekly competitive intelligence report.\n\n"
            f"The report must include:\n"
            f"1. Executive Summary (3-4 sentences, most critical insights only)\n"
            f"2. Key Developments (ranked high to low significance, all companies)\n"
            f"3. Competitive Comparison (who moved most, biggest threats and opportunities)\n"
            f"4. SWOT Summary (one line per company)\n"
            f"5. Weak Signals (early indicators of strategic shifts with recommended actions)\n"
            f"6. 30-Day Outlook\n\n"
            f"Write for a CEO/CTO audience. Be specific, concise, and actionable."
        ),
        expected_output=(
            f"A complete competitive intelligence report as a JSON object with sections: "
            f"executive_summary, key_developments (array), competitive_comparison (object), "
            f"swot_summary (array), weak_signals (array), outlook_30_days (string). "
            f"Professional business language. No fabricated data."
        ),
        agent=agent,
        context=context_tasks or [],
    )
