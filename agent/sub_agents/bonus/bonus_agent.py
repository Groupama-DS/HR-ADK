import os
from google.adk.agents import LlmAgent
from ...tools.bonus_rag_tool import bonus_rag_tool, bonus_datastore_tool
from agent.constants import MODEL

# Read the prompt
with open(os.path.join(os.path.dirname(__file__), 'bonus_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

bonus_agent = LlmAgent(
    model=MODEL,
    name='bonus_agent',
    instruction=prompt,
)