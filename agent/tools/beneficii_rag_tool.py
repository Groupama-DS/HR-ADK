from .custom_search_tool import CustomVertexAiSearchTool
from ..constants import PROJECT_ID, LOCATION, BENEFICII_ENGINE_ID

beneficii_datastore_tool = CustomVertexAiSearchTool(
    name="beneficii_search_tool",
    description="This tool is used to search answers for questions about benefits",
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{BENEFICII_ENGINE_ID}"
)
