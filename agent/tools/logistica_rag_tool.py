import os
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from agent.constants import LOGISTICA_DATASTORE

logistica_datastore_tool = VertexAiSearchTool(
    data_store_id=LOGISTICA_DATASTORE
)
