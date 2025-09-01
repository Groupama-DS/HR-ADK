from .custom_search_tool import CustomVertexAiSearchTool
from ..constants import PROJECT_ID, LOCATION, TRAINING_ENGINE_ID

training_datastore_tool = CustomVertexAiSearchTool(
    name="training_search_tool",
    description="This tool is used to search answers for questions about training",
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{TRAINING_ENGINE_ID}"
)
