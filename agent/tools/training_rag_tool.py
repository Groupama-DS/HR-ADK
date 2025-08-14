import os
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from agent.constants import PROJECT_ID, LOCATION, TRAINING_ENGINE_ID

training_datastore_tool = VertexAiSearchTool(
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{TRAINING_ENGINE_ID}"
)
