from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools import FunctionTool
from typing import Optional

def init_state(callback_context: CallbackContext) -> Optional[LlmResponse]:
    state_key="pachet_asigurare"
    if state_key not in callback_context.state:
        callback_context.state[state_key] = "nespecificat"

    return None
