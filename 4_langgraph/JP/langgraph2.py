from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from typing import Annotated
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import Tool
import os
import requests
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition
from IPython.display import Image, display


load_dotenv(override = True)

serper = GoogleSerperAPIWrapper()

tool_search = Tool(name="search", func=serper.run, description="Use this tool when you need to search the internet")

print(tool_search.invoke("what is weather today in Atlanta?"))

pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_url = "https://api.pushover.net/1/messages.json"

def push(text: str):
    """Send a push notification to the user"""
    requests.post(pushover_url, data = {"token": pushover_token, "user": pushover_user, "message": text})

tool_push = Tool(name="push", func=push, description="Use this tool when you need to send a push notification to the user")
print(tool_push.invoke("Hello, I am a push notification"))

tools = [tool_search, tool_push]

class State(BaseModel):
    messages: Annotated[list, add_messages]


graph =  StateGraph(State)

llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph.add_node("chatbot", chatbot)
graph.add_node("tools", ToolNode(tools = tools))

graph.add_conditional_edges("chatbot", tools_condition, "tools")
graph.add_edge("tools", "chatbot")
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

graph = graph.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

graph.invoke({"messages":[{"role":"user", "content":"what is weather in Atlanta?"}]})