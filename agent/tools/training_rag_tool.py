import os
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from agent.constants import TRAINING_DATASTORE

training_datastore_tool = VertexAiSearchTool(
    data_store_id=TRAINING_DATASTORE,
)
