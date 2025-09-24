from .custom_search_tool import CustomVertexAiSearchTool
from ..constants import PROJECT_ID, LOCATION, FULL_ENGINE_ID, TRAINING_DATASTORE
from google.adk.tools import VertexAiSearchTool
from google.genai.types import VertexAISearchDataStoreSpec

training_datastore_tool = VertexAiSearchTool(
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{FULL_ENGINE_ID}",
    data_store_specs=[VertexAISearchDataStoreSpec(
        data_store=TRAINING_DATASTORE,
    )],
)
