
import os
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from dotenv import load_dotenv

load_dotenv()

ami_rag_tool = VertexAiRagRetrieval(
    name='ami_rag_tool',
    description=(
        "Use this tool to answer user's questions about medical inurance coverage and procedures from the RAG corpus"
    ),
    rag_resources=[
        rag.RagResource(
            rag_corpus=os.environ.get("AMI_RAG_CORPUS")
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)