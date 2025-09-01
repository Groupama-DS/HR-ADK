from .custom_search_tool import CustomVertexAISearchTool
from agent.constants import PROJECT_ID, LOCATION, AMI_ENGINE_ID

ami_datastore_tool = CustomVertexAISearchTool(
    name="ami_search_tool",
    description="this tool is used to search answers for questions about medical insurance",
    search_engine_id=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{AMI_ENGINE_ID}"
)