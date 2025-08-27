# In your callbacks/state_callback.py

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from typing import Optional

def save_grounding_metadata_to_state(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    An after_model_callback that checks the LlmResponse for grounding_metadata
    and saves it to the session state.
    """
    if llm_response.grounding_metadata:
        metadata = llm_response.grounding_metadata
        callback_context.state['last_grounding_metadata'] = metadata.model_dump()
    else:
        # If this model call had no metadata, clear any old metadata
        # to prevent it from being accidentally used in a later turn.
        if 'last_grounding_metadata' in callback_context.state:
            del callback_context.state['last_grounding_metadata']
        
    # Always return None to allow the agent to continue its normal flow.
    return None