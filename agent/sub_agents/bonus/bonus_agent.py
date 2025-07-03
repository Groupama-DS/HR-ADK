import os

from google.adk.agents import Agent
from ...tools.bonus_rag_tool import bonus_rag_tool
from .bonus_prompt import PROMPT

from dotenv import load_dotenv
load_dotenv()


bonus_agent = Agent(
    model=os.environ.get("MODEL"),
    name='bonus_agent',
    instruction=PROMPT,
    tools=[
        bonus_rag_tool,
    ]
)