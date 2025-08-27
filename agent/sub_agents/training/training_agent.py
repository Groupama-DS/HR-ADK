import os
from google.adk.agents import LlmAgent
from ...tools.training_rag_tool import training_datastore_tool
from agent.constants import MODEL
from ...callbacks.grounding_callback import save_grounding_metadata_to_state

# Read the prompt
with open(os.path.join(os.path.dirname(__file__), 'training_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

training_agent = LlmAgent(
    model=MODEL,
    name='training_agent',
    instruction=prompt,
    tools=[
        training_datastore_tool,
    ],
    after_model_callback=save_grounding_metadata_to_state
)
