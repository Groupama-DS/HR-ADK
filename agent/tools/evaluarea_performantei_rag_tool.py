import os
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from agent.constants import EVALUAREA_PERFORMANTEI_DATASTORE

evaluarea_performantei_datastore_tool = VertexAiSearchTool(
    data_store_id=EVALUAREA_PERFORMANTEI_DATASTORE
)
