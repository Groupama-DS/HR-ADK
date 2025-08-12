
import os
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from vertexai.preview import rag
from agent.constants import BONUS_DATASTORE

bonus_rag_tool = VertexAiRagRetrieval(
    name='bonus_rag_tool',
    description=(
        "Use this tool to answer user's questions about bonuses, payments and related procedures."
    ),
    rag_resources=[
        rag.RagResource(
            rag_corpus=os.environ.get("BONUS_RAG_CORPUS")
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

bonus_datastore_tool = VertexAiSearchTool(
    data_store_id=BONUS_DATASTORE,
)