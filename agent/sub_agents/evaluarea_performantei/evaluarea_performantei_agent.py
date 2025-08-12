import os
from google.adk.agents import LlmAgent
from ...tools.evaluarea_performantei_rag_tool import evaluarea_performantei_datastore_tool
from agent.constants import MODEL

# Read the prompt
with open(os.path.join(os.path.dirname(__file__), 'evaluarea_performantei_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

evaluarea_performantei_agent = LlmAgent(
    model=MODEL,
    name='evaluarea_performantei_agent',
    instruction=prompt,
    tools=[
        evaluarea_performantei_datastore_tool,
    ]
)
