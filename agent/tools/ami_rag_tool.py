
import os
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from vertexai.preview import rag
from agent.constants import PROJECT_ID, LOCATION, AMI_ENGINE_ID

ami_datastore_tool = VertexAiSearchTool(
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{AMI_ENGINE_ID}"
)