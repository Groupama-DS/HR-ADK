from .custom_search_tool import CustomVertexAiSearchTool
from ..constants import PROJECT_ID, LOCATION, TRAINING_ENGINE_ID
from google.adk.tools import VertexAiSearchTool

training_datastore_tool = VertexAiSearchTool(
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{TRAINING_ENGINE_ID}"
)
