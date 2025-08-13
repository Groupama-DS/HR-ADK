
import os
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from vertexai.preview import rag
from agent.constants import AMI_DATASTORE, PROJECT_ID, LOCATION, TEST_ENGINE_ID

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
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{TEST_ENGINE_ID}"
)