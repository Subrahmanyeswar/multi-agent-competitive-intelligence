import logging
from crewai import Crew, Process
from agents.research_agent import ResearchAgentBuilder
from agents.manager_agent import (
    build_manager_agent,
    build_analysis_crewai_agent,
    build_synthesizer_crewai_agent,
)
from tasks.research_task import create_research_task
from tasks.analysis_task import create_analysis_task
from tasks.synthesis_task import create_synthesis_task
from config.settings import settings

logger = logging.getLogger(__name__)

class IntelligenceCrew:
    """
    Assembles and runs the full multi-agent crew using CrewAI's
    hierarchical process with a Manager Agent coordinating specialists.
    """
    
    def __init__(self):
        self.competitors = settings.load_competitors()
        self.researcher_builder = ResearchAgentBuilder()
        
    def build_and_run(self) -> dict:
        """
        Build all agents, create all tasks, assemble crew, and kick off.
        Returns the raw crew output as a string.
        """
        logger.info("[Crew] Building agents...")
        
        # Build all research agents (one per competitor)
        research_agents = []
        research_tasks = []
        
        for company in self.competitors:
            agent = self.researcher_builder.build(company)
            task = create_research_task(company, agent)
            research_agents.append(agent)
            research_tasks.append(task)
        
        # Build analysis agent and tasks
        analysis_agent = build_analysis_crewai_agent()
        analysis_tasks = []
        
        for company in self.competitors:
            task = create_analysis_task(
                company_name=company["name"],
                agent=analysis_agent,
                context_tasks=research_tasks,
            )
            analysis_tasks.append(task)
        
        # Build synthesizer agent and task
        synthesizer_agent = build_synthesizer_crewai_agent()
        company_names = [c["name"] for c in self.competitors]
        synthesis_task = create_synthesis_task(
            companies=company_names,
            agent=synthesizer_agent,
            context_tasks=analysis_tasks,
        )
        
        # Build manager agent
        manager = build_manager_agent()
        
        # All tasks in order
        all_tasks = research_tasks + analysis_tasks + [synthesis_task]
        all_agents = research_agents + [analysis_agent, synthesizer_agent]
        
        logger.info(f"[Crew] Assembling crew with {len(all_agents)} agents and {len(all_tasks)} tasks")
        
        crew = Crew(
            agents=all_agents,
            tasks=all_tasks,
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True,
            memory=False,
        )
        
        logger.info("[Crew] Kicking off crew run...")
        result = crew.kickoff()
        
        logger.info("[Crew] Crew run complete")
        return result
