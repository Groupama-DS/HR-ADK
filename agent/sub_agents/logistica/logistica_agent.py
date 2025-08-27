import os
from google.adk.agents import LlmAgent
from ...tools.logistica_rag_tool import logistica_datastore_tool
from agent.constants import MODEL
from ...callbacks.grounding_callback import save_grounding_metadata_to_state

# Read the prompt
with open(os.path.join(os.path.dirname(__file__), 'logistica_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

logistica_agent = LlmAgent(
    model=MODEL,
    name='logistica_agent',
    instruction=prompt,
    tools=[
        logistica_datastore_tool,
    ],
    after_model_callback=save_grounding_metadata_to_state
)
