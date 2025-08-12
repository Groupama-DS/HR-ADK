import os
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from agent.constants import BENEFICII_DATASTORE

beneficii_datastore_tool = VertexAiSearchTool(
    data_store_id=BENEFICII_DATASTORE
)
