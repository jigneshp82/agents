from crewai import Agent, Crew, Process, Task
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from markdown_it.rules_inline import entity
from pydantic import BaseModel, Field
from crewai_tools import SerperDevTool
from crewai.memory import LongTermMemory,ShortTermMemory,EntityMemory

from src.stock_picker.tools.push_notification_tool import NotificationTool


class TrendingCompany(BaseModel):
    """ A company that is in the news and attracting attention """
    name:str = Field(description = 'Company Name')
    ticker:str = Field(description = 'Company ticker symbol')
    reason:str = Field(description = 'Reason this Company is trending in the news')

class TrendingCompanyList(BaseModel):
    """ List of multiple trending companies that are in the news """
    companies: List[TrendingCompany] = Field(description = 'list of the trending companies in the news')

class TrendingCompanyResearch(BaseModel):
    """ Detailed research on a company """
    name:str = Field(description='Company Name')
    market_position:str = Field(description = 'Current Market value and compatitive analysis')
    future_outlook:str = Field(description = 'Future outlook and groth prospect')
    investment_potential:str =Field(description = 'Investment potential and suitability for investment')

class TrendingCompanyResearchList(BaseModel):
    """ A list of detailed research on all the companies """
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")

@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(config = self.agents_config['trending_company_finder'], tools = [SerperDevTool()], memory = True)

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(config = self.agents_config['financial_researcher'], tools = [SerperDevTool()])

    @agent
    def stock_picker(self) -> Agent:
        return Agent(config = self.agents_config['stock_picker'], tools=[NotificationTool()], memory = True)
        #return Agent(config = self.agents_config['stock_picker'])

    @task
    def find_trending_companies(self) -> Task:
        return Task(config = self.tasks_config['find_trending_companies'], output_pydantic = TrendingCompanyList)


    @task
    def research_trending_companies(self) -> Task:
        return Task(config = self.tasks_config['research_trending_companies'], output_pydantic = TrendingCompanyResearchList)


    @task
    def pick_best_company(self) -> Task:
        return Task(config = self.tasks_config['pick_best_company'])

    @crew
    def crew(self) -> Crew:
        manager_agent = Agent(config = self.agents_config['manager'], allow_delegation = True)
        short_term_memory = ShortTermMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider" : "openai",
                    "model" : ["text-embedding-3-small"]
                },
                type='short-term',
                path = "./memory/"
            )
        )
        entity_memory = EntityMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai",
                    "model": ["text-embedding-3-small"]
                },
                type='short-term',
                path="./memory/"
            )
        )

        long_term_memory = LongTermMemory(
            storage= LTMSQLiteStorage( db_path= "./memory/long_term_memory.db")
        )

        return Crew(
            agents = self.agents,
            tasks = self.tasks,
            process = Process.hierarchical ,
            manager_agent =manager_agent,
            verbose = True,
            memory = True,
            short_term_memory=short_term_memory,
            long_term_memory=long_term_memory,
            entity_memory=entity_memory
        )