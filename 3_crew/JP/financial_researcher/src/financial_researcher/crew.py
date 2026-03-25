from multiprocessing import process
from tabnanny import verbose
from pydantic import config
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from typing import List


@CrewBase
class FinancialResearcher():
    """FinancialResearcher crew"""

    #agents: List[BaseAgent]
    #tasks: List[Task]
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def researcher(self) -> Agent:
        print (self.agents_config['researcher'])
        return Agent(config =self.agents_config['researcher'], verbose = True, tools = [SerperDevTool()])

    @agent
    def analyst(self) -> Agent:
        return Agent(config = self.agents_config['analyst'], verbose = True)

    @task
    def research_task(self) -> Task:
        return Task(config = self.tasks_config['research_task'], verbose = True)

    @task
    def analysis_task(self) -> Task:
        return Task(config = self.tasks_config['analysis_task'],verbose = True)

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents = self.agents,
            tasks = self.tasks,
            process = Process.sequential,
            Verbose = True
        )
