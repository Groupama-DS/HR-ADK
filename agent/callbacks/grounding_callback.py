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
    print(f"--- Running after_model_callback for {callback_context.agent_name} ---")
    
    if llm_response.grounding_metadata:
        metadata = llm_response.grounding_metadata
        print("--- Found grounding_metadata directly in LlmResponse ---")
        
        # Save the serializable version of the metadata to the state.
        callback_context.state['last_grounding_metadata'] = metadata.model_dump()
        print("--- Saved grounding_metadata to session state ---")
    else:
        # If this model call had no metadata, clear any old metadata
        # to prevent it from being accidentally used in a later turn.
        if 'last_grounding_metadata' in callback_context.state:
            del callback_context.state['last_grounding_metadata']
        print("--- No grounding_metadata found in this LlmResponse ---")
        
    # Always return None to allow the agent to continue its normal flow.
    return None