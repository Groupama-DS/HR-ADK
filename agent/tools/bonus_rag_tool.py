
import os
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from vertexai.preview import rag

from dotenv import load_dotenv

load_dotenv()

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
    data_store_id="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/bonus-remunerare-v6_1750949303418",
)