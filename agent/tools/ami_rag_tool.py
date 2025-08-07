
import os
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool

from vertexai.preview import rag

from dotenv import load_dotenv

load_dotenv()

ami_rag_tool = VertexAiRagRetrieval(
    name='ami_rag_tool',
    description=(
        "Tool-ul contine un corpus cu documente nestructurate care sunt folosite pentur a raspunde la intrebari despre asigurarea medicala si ce servicii medicale sunt incluse in anumite pachete de sanatate."
    ),
    rag_resources=[
        rag.RagResource(
            rag_corpus=os.environ.get("AMI_RAG_CORPUS_V2")
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.1,
)

ami_datastore_tool = VertexAiSearchTool(
    data_store_id="projects/prj-hackathon-team2/locations/eu/collections/default_collection/dataStores/ami-main-docs_1750757232003",
)