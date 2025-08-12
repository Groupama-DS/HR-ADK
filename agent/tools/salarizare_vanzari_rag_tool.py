import os
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from agent.constants import SALARIZARE_VANZARI_DATASTORE

salarizare_vanzari_datastore_tool = VertexAiSearchTool(
    data_store_id=SALARIZARE_VANZARI_DATASTORE
)
