import os
from google.adk.agents import LlmAgent
from ...tools.beneficii_rag_tool import beneficii_datastore_tool
from agent.constants import MODEL

# Read the prompt
with open(os.path.join(os.path.dirname(__file__), 'beneficii_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

beneficii_agent = LlmAgent(
    model=MODEL,
    name='beneficii_agent',
    instruction=prompt,
    tools=[
        beneficii_datastore_tool,
    ]
)
