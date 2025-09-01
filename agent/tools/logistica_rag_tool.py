from .custom_search_tool import CustomVertexAiSearchTool
from ..constants import PROJECT_ID, LOCATION, LOGISTICA_ENGINE_ID
from google.adk.tools import VertexAiSearchTool

logistica_datastore_tool = VertexAiSearchTool(
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{LOGISTICA_ENGINE_ID}"
)
