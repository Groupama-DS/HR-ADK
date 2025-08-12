import os
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from agent.constants import RELATII_MUNCA_DATASTORE

relatii_munca_datastore_tool = VertexAiSearchTool(
    data_store_id=RELATII_MUNCA_DATASTORE
)
