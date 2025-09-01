from .custom_search_tool import CustomVertexAISearchTool
from agent.constants import PROJECT_ID, LOCATION, EVALUAREA_PERFORMANTEI_ENGINE_ID

evaluarea_performantei_datastore_tool = CustomVertexAISearchTool(
    name="evaluarea_performantei_search_tool",
    description="This tool is used to search answers for questions about performance evaluation",
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{EVALUAREA_PERFORMANTEI_ENGINE_ID}"
)
