import os
import json
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool
from config.settings import SERPER_API_KEY, OPENAI_API_KEY, OPENAI_MODEL
from .crew_models import (
    OutlineStructure, 
    InitialResearch, 
    CaseStudy, 
    InitialReferenceChecker, 
    PeerReviewFeedback, 
    MainResearch
)

from .crew_output import (
    outline_output, 
    initialResearch_output, 
    case_study_output, 
    InitialReferenceChecker_output, 
    mainResearch_output, 
    peer_review_output, 
    final_output
)

# Setting up the toolings

OPENAI_API_KEY = OPENAI_API_KEY
SERPER_API_KEY = SERPER_API_KEY

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
web_rag_tool = WebsiteSearchTool()

# Setting up the crew

@CrewBase
class ResearchCrew:
    """Research crew"""
    agents_config = os.path.join('..', 'config', 'agents.yaml')
    tasks_config = os.path.join('..', 'config', 'tasks.yaml')

    @agent
    def outline_concepter(self) -> Agent:
        return Agent(
            config=self.agents_config['outline_concepter'],
            verbose=True,
            allow_delegation=False,
            output_log_file=True,
            model=OPENAI_MODEL
        )

    @agent
    def initial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['initial_researcher'],
            tools=[search_tool, scrape_tool, web_rag_tool],
            verbose=True,
            allow_delegation=False,
            output_log_file=True,
            model=OPENAI_MODEL
        )
    
    @agent
    def case_study_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['case_study_specialist'],
            tools=[search_tool, scrape_tool, web_rag_tool],
            verbose=True,
            allow_delegation=False,
            output_log_file=True,
            model=OPENAI_MODEL
        )
    
    @agent
    def reference_checker_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['reference_checker_specialist'],
            verbose=True,
            allow_delegation=False,
            output_log_file=True,
            model=OPENAI_MODEL
        )

    @agent
    def main_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['main_researcher'],
            tools=[search_tool, scrape_tool, web_rag_tool],
            verbose=True,
            allow_delegation=False,
            output_log_file=True,
            model=OPENAI_MODEL
        )
    
    @agent
    def peer_review_simulator(self) -> Agent:
        return Agent(
            config=self.agents_config['peer_review_simulator'],
            tools=[search_tool, scrape_tool, web_rag_tool],
            verbose=True,
            allow_delegation=False,
            output_log_file=True,
            model=OPENAI_MODEL
        )

    @agent
    def final_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['final_editor'],
            tools=[search_tool, scrape_tool, web_rag_tool],
            verbose=True,
            allow_delegation=False,
            output_log_file=True,
            model=OPENAI_MODEL
        )

    @task
    def outline_task(self) -> Task:
        return Task(
            config=self.tasks_config['outline_task'],
            agent=self.outline_concepter(),
            expected_output = outline_output,
            output_json=OutlineStructure
        )

    @task
    def initial_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['initial_research_task'],
            agent=self.initial_researcher(),
            expected_output = initialResearch_output,
            context=[self.outline_task()],
            output_json=InitialResearch,
            # output_file = "initial.json"
        )
    
    @task
    def case_study_task(self) -> Task:
        return Task(
            config=self.tasks_config['case_study_task'],
            agent=self.case_study_specialist(),
            expected_output = case_study_output,
            context=[self.initial_research_task()],
            output_json=CaseStudy,
            # output_file = "case.json"
        )
    
    @task
    def reference_checker_task(self) -> Task:
        return Task(
            config=self.tasks_config['reference_checker_task'],
            agent=self.reference_checker_specialist(),
            expected_output = InitialReferenceChecker_output,
            context=[self.initial_research_task(), self.case_study_task()],
            output_json=InitialReferenceChecker,
            # output_file = "refcheck.json"
        )

    @task
    def main_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['main_research_task'],
            agent=self.main_researcher(),
            expected_output = mainResearch_output,
            context=[self.reference_checker_task()],
            output_json=MainResearch,
            # output_file = "main.json"
        )
    
    @task
    def peer_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['peer_review_task'],
            agent=self.peer_review_simulator(),
            expected_output = peer_review_output,
            context=[self.main_research_task()],
            output_json=PeerReviewFeedback
        )

    @task
    def final_edit_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_edit_task'],
            agent=self.final_editor(),
            expected_output = final_output,
            context=[self.main_research_task(), self.peer_review_task()],
            output_json=MainResearch,
            output_file = "final_research.json"
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,  # Or use Process.hierarchical if needed
            verbose=2
        )

# Patch the _save_file method in the Task class
def patched_save_file(self, result):
    with open(self.output_file, 'w') as file:
        if isinstance(result, dict):
            file.write(json.dumps(result, indent=2))
        else:
            file.write(result)

Task._save_file = patched_save_file