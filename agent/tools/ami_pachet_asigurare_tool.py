from google.adk.tools import ToolContext # Or CallbackContext
from google.adk.tools import FunctionTool

def set_pachet_asigurare(tool_context: ToolContext, pachet_asigurare: str) -> dict:
    """
    takes pachet_asigurare from user interaction and puts it in state
    
    Args:
        pachet_asigurare: numele pachetului de asigurare medicala al utilizatorului
    """
    state_key = "pachet_asigurare"
    tool_context.state[state_key] = pachet_asigurare
    print(f"Set pachet_asigurare to '{pachet_asigurare}'")

    return {
        "status": "success",
        "pachet_asigurare": pachet_asigurare,
    }



pachet_asigurare_tool = FunctionTool(func=set_pachet_asigurare)