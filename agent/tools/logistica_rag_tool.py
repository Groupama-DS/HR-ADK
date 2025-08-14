import os
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from agent.constants import PROJECT_ID, LOCATION, LOGISTICA_ENGINE_ID

logistica_datastore_tool = VertexAiSearchTool(
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{LOGISTICA_ENGINE_ID}"
)
