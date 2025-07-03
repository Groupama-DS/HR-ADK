import os

from google.adk.agents import Agent
from ...tools.bonus_rag_tool import bonus_rag_tool

from dotenv import load_dotenv
load_dotenv()

# Read the prompt
with open(os.path.join(os.path.dirname(__file__), 'bonus_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

bonus_agent = Agent(
    model=os.environ.get("MODEL"),
    name='bonus_agent',
    instruction=prompt,
    tools=[
        bonus_rag_tool,
    ]
)