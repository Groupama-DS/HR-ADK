import os

from google.adk.agents import Agent
from ...tools.ami_rag_tool import ami_rag_tool
from .ami_prompt import PROMPT

from dotenv import load_dotenv
load_dotenv()

ami_agent = Agent(
    model=os.environ.get("MODEL"),
    name='ami_agent',
    instruction=PROMPT,
    tools=[
        ami_rag_tool,
    ]
)

