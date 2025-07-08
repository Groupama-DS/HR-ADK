import os

from google.adk.agents import Agent
from ...tools.ami_rag_tool import ami_rag_tool, ami_datastore_tool

from dotenv import load_dotenv
load_dotenv()

# Read the prompt
with open(os.path.join(os.path.dirname(__file__), 'ami_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

ami_agent = Agent(
    model=os.environ.get("MODEL"),
    name='ami_agent',
    instruction=prompt,
    tools=[
        ami_datastore_tool,
    ]
)

