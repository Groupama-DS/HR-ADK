from .custom_search_tool import CustomVertexAiSearchTool
from ..constants import PROJECT_ID, LOCATION, SALARIZARE_VANZARI_ENGINNE_ID

salarizare_vanzari_datastore_tool = CustomVertexAiSearchTool(
    name="salarizare_vanzari_search_tool",
    description="This tool is used to search answers for questions about salary and sales",
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{SALARIZARE_VANZARI_ENGINNE_ID}"
)
