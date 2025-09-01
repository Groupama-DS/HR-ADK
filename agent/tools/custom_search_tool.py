from __future__ import annotations
from typing import Optional
from google.genai import types
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool

class CustomVertexAISearchTool(VertexAiSearchTool):
  """A custom Vertex AI Search tool that allows overriding the name and description."""

  def __init__(
      self,
      *,
      name: str,
      description: str,
      data_store_id: Optional[str] = None,
      data_store_specs: Optional[
          list[types.VertexAISearchDataStoreSpec]
      ] = None,
      search_engine_id: Optional[str] = None,
      filter: Optional[str] = None,
      max_results: Optional[int] = None,
  ):
    """Initializes the custom Vertex AI Search tool.

    Args:
      name: The name of the tool.
      description: The description of the tool.
      data_store_id: The Vertex AI search data store resource ID in the format
        of
        "projects/{project}/locations/{location}/collections/{collection}/dataStores/{dataStore}".
      data_store_specs: Specifications that define the specific DataStores to be
        searched. It should only be set if engine is used.
      search_engine_id: The Vertex AI search engine resource ID in the format of
        "projects/{project}/locations/{location}/collections/{collection}/engines/{engine}".
      filter: The filter to apply to the search.
      max_results: The maximum number of results to return.
    """
    super().__init__(
        data_store_id=data_store_id,
        data_store_specs=data_store_specs,
        search_engine_id=search_engine_id,
        filter=filter,
        max_results=max_results,
    )
    self.name = name
    self.description = description