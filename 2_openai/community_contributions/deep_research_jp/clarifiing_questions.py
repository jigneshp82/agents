from pydantic import BaseModel, Field
from agents import Agent

NO_OF_QUESTIONS = 3
INSTRUCTIONS = "You are a research assistant. Your task is to ask 3 clarifying questions that help refine and understand \
        a research query better. After the user answers them, hand off control to the Research Coordinator to perform the full research."

class Questions(BaseModel):
    questions:list[str] = Field(description = f"{NO_OF_QUESTIONS} clarifying questions to better understand the research topic")

clarifiing_agent = Agent(name = "clarifying question Agent",
instructions= INSTRUCTIONS,
output_type=Questions,
model = "gpt-4o-mini")