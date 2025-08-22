import os
from google.adk.agents import LlmAgent
from ...tools.ami_rag_tool import ami_datastore_tool
from ...tools.ami_pachet_asigurare_tool import pachet_asigurare_tool
from ...callbacks.grounding_callback import save_grounding_metadata_to_state
from agent.constants import MODEL

# Read the prompt
with open(os.path.join(os.path.dirname(__file__), 'ami_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

ami_agent = LlmAgent(
    model=MODEL,
    name='ami_agent',
    instruction=prompt,
    tools=[
        ami_datastore_tool,
    ],
    after_model_callback=save_grounding_metadata_to_state
)

