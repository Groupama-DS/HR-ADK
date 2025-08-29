# import os
# from langchain_google_vertexai import ChatVertexAI
# from langchain_community.retrievers.google_vertex_ai_search import GoogleVertexAISearchRetriever
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.tools import Tool
# from dotenv import load_dotenv

# load_dotenv()

# # --- Configuration ---
# PROJECT_ID = "prj-hackathon-team2"
# LOCATION_ID = "eu"

# # Set environment variables for authentication (if not already configured)
# # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/your/service_account.json"
# # If running in Google Colab, uncomment and run:
# # from google.colab import auth as google_auth
# # google_auth.authenticate_user()

# # 1. Initialize VertexAISearchRetriever as the search tool
# AMI_ENGINE_ID = "asigurare-medicala_1755091622568"
# SEARCH_ENGINE_ID = "projects/prj-hackathon-team2/locations/eu/collections/default_collection/engines/asigurare-medicala_1755091622568"


# query = "am inclus rmn in asigurarea medicala?"
# retriever = GoogleVertexAISearchRetriever(
#     project_id=PROJECT_ID,
#     location_id=LOCATION_ID,
#     search_engine_id=SEARCH_ENGINE_ID,
#     max_documents=3,
#     engine_data_type=0,
# )

# result = retriever.invoke(query)
# for doc in result:
#     print(doc)

