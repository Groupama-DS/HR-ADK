from .custom_search_tool import CustomVertexAiSearchTool
from ..constants import PROJECT_ID, LOCATION, RELATII_MUNCA_ENGINE_ID

relatii_munca_datastore_tool = CustomVertexAiSearchTool(
    name="relatii_munca_search_tool",
    description="This tool is used to search answers for questions about work relations",
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{RELATII_MUNCA_ENGINE_ID}"
)
