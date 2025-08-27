import os
from google.adk.agents import LlmAgent
from ...tools.relatii_munca_rag_tool import relatii_munca_datastore_tool
from agent.constants import MODEL
from ...callbacks.grounding_callback import save_grounding_metadata_to_state

# Read the prompt
with open(os.path.join(os.path.dirname(__file__), 'relatii_munca_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

relatii_munca_agent = LlmAgent(
    model=MODEL,
    name='relatii_munca_agent',
    instruction=prompt,
    tools=[
        relatii_munca_datastore_tool,
    ],
    after_model_callback=save_grounding_metadata_to_state
)
