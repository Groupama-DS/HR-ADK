from .custom_search_tool import CustomVertexAiSearchTool
from ..constants import PROJECT_ID, LOCATION, BENEFICII_ENGINE_ID
from google.adk.tools import VertexAiSearchTool

beneficii_datastore_tool = VertexAiSearchTool(
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{BENEFICII_ENGINE_ID}"
)
