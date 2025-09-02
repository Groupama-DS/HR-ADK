from .custom_search_tool import CustomVertexAiSearchTool
from ..constants import PROJECT_ID, LOCATION, SALARIZARE_VANZARI_ENGINNE_ID, FULL_ENGINE_ID, SALARIZARE_VANZARI_DATASTORE
from google.adk.tools import VertexAiSearchTool
from google.genai.types import VertexAISearchDataStoreSpec

salarizare_vanzari_datastore_tool = VertexAiSearchTool(
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{FULL_ENGINE_ID}",
    data_store_specs=[VertexAISearchDataStoreSpec(
        data_store=SALARIZARE_VANZARI_DATASTORE,
    )],
)
