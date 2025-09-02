from .custom_search_tool import CustomVertexAiSearchTool
from ..constants import PROJECT_ID, LOCATION, EVALUAREA_PERFORMANTEI_ENGINE_ID, FULL_ENGINE_ID, EVALUAREA_PERFORMANTEI_DATASTORE
from google.adk.tools import VertexAiSearchTool
from google.genai.types import VertexAISearchDataStoreSpec

evaluarea_performantei_datastore_tool = VertexAiSearchTool(
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{FULL_ENGINE_ID}",
        data_store_specs=[VertexAISearchDataStoreSpec(
        data_store=EVALUAREA_PERFORMANTEI_DATASTORE,
    )],
)
