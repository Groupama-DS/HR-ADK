from .custom_search_tool import CustomVertexAiSearchTool
from ..constants import PROJECT_ID, LOCATION, SALARIZARE_VANZARI_ENGINNE_ID
from google.adk.tools import VertexAiSearchTool

salarizare_vanzari_datastore_tool = VertexAiSearchTool(
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{SALARIZARE_VANZARI_ENGINNE_ID}"
)
