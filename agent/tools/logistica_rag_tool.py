from .custom_search_tool import CustomVertexAISearchTool
from agent.constants import PROJECT_ID, LOCATION, LOGISTICA_ENGINE_ID

logistica_datastore_tool = CustomVertexAISearchTool(
    name="logistica_search_tool",
    description="This tool is used to search answers for questions about logistics",
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{LOGISTICA_ENGINE_ID}"
)
