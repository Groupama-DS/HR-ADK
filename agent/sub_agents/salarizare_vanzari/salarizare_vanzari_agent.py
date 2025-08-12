import os
from google.adk.agents import LlmAgent
from ...tools.salarizare_vanzari_rag_tool import salarizare_vanzari_datastore_tool
from agent.constants import MODEL

# Read the prompt
with open(os.path.join(os.path.dirname(__file__), 'salarizare_vanzari_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

salarizare_vanzari_agent = LlmAgent(
    model=MODEL,
    name='salarizare_vanzari_agent',
    instruction=prompt,
    tools=[
        salarizare_vanzari_datastore_tool,
    ]
)
