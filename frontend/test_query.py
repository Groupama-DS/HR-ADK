import os
import json
from dotenv import load_dotenv
import asyncio

# Load environment variables and initialize Vertex AI
load_dotenv()

import vertexai
from vertexai import agent_engines


project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
location = os.environ["GOOGLE_CLOUD_LOCATION"]
app_name = "menu_agent"
bucket_name = os.environ["GOOGLE_CLOUD_STORAGE_BUCKET"]


# Initialize Vertex AI with the correct project and location
vertexai.init(
    project=project_id,
    location=location,
    staging_bucket=bucket_name,
)

# Filter agent engines by the app name in .env
ae_apps = agent_engines.list(filter=f'display_name="{app_name}"')
remote_app = next(ae_apps)

print(f"Using remote app: {remote_app.display_name}")

prompt = """
    Am inclus rmn in asigurare?
"""

async def main():
    # SOLUȚIA: Folosește 'await' pentru a obține dicționarul sesiunii
    remote_session = await remote_app.async_create_session(user_id="u_457")

    # SOLUȚIA: Accesează ID-ul folosind notația pentru dicționar ('['id']')
    async for event in remote_app.async_stream_query(
        user_id="u_457",
        session_id=remote_session["id"], # Corectat înapoi la notația cu paranteze
        message=prompt,
    ):
        print("start")
        print("------ NEW EVENT ------")

        # Logica pentru afișarea evenimentului rămâne aceeași
        try:
            print(json.dumps(event, indent=2, ensure_ascii=False, default=str))
        except TypeError:
            print(event)

        # Eroarea inițială era 'AttributeError: 'dict' object has no attribute 'content''
        # Vom verifica tipul evenimentului pentru a evita erori viitoare.
        # Obiectele de eveniment returnate de SDK ar trebui să fie obiecte, nu dicționare.
        # Dacă eroarea persistă, înseamnă că 'event' este un dicționar.
        if hasattr(event, 'content') and event.content and event.content.parts:
            if hasattr(event, 'get_function_calls') and event.get_function_calls():
                print("  Type: Tool Call Request")
            elif hasattr(event, 'get_function_responses') and event.get_function_responses():
                print("  Type: Tool Result")
            elif event.content.parts[0].text:
                if hasattr(event, 'partial') and event.partial:
                    print("  Type: Streaming Text Chunk")
                else:
                    print("  Type: Complete Text Message")
            else:
                print("  Type: Other Content (e.g., code result)")
        elif hasattr(event, 'actions') and event.actions and (hasattr(event.actions, 'state_delta') or hasattr(event.actions, 'artifact_delta')):
            print("  Type: State/Artifact Update")
        else:
             # Dacă este un dicționar, afișăm cheile pentru a ajuta la depanare
            if isinstance(event, dict):
                 print(f"  Type: Dictionary Event with keys: {event.keys()}")
            else:
                 print("  Type: Control Signal or Other")


if __name__ == "__main__":
    asyncio.run(main())