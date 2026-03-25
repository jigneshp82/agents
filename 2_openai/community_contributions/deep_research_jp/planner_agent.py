

from pydantic import BaseModel, Field
from agents import Agent


SEARCHES = 5

agent_instruction = f"You are a helpfule reseach assistance. Givern a query, come up with set of web searches, to answer best possible \
way to the query. Limit Ouput to {SEARCHES} terms to query for"

class WebSearchItem(BaseModel):
    query:str = Field(description="The Search Term to use for the web searh")
    reason:str = Field(description="This signifies reason why this result is imprtant for given search query")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A List of web searches to get best answer for given query")

planner_agent = Agent(
    name = "Planner Agent",
    instructions=agent_instruction,
    output_type=WebSearchPlan,
    model = "gpt-4o-mini",
)