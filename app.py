import gradio as gr
import os
from agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

from app_utils import CUSTOM_CSS, generate_download_signed_url_v4

# Bypass the system proxy for localhost communication.
os.environ['NO_PROXY'] = '127.0.0.1,localhost'

# Set up session service and runner
session_service = InMemorySessionService()
runner = Runner(
    app_name="GroupamaAgent",
    agent=root_agent,
    session_service=session_service,
)
user_id = "demo_user"
session = None
session_id = None

def create_sources_html(grounding_metadata):
    """Generates the HTML for the source cards, wrapped in a collapsible <details> tag."""
    if not grounding_metadata or 'grounding_chunks' not in grounding_metadata or not grounding_metadata['grounding_chunks']:
        return ""

    cards_html = ""
    for chunk in grounding_metadata['grounding_chunks']:
        retrieved_context = chunk.get('retrieved_context', {})
        title = retrieved_context.get('title', 'Source Document')
        uri = retrieved_context.get('uri', '#')
        text_content = retrieved_context.get('text', 'No content available.')

        # Extract bucket and blob name from gs:// URI
        signed_url = "#"
        if uri.startswith("gs://"):
            try:
                # Split the URI into bucket and blob name
                # Example: gs://hackathon_hr_minds/Asigurare_Medicala/RM_AMI/Lista%20servicii%20medicale%20ambulatorii_adulti%20GAM.pdf
                path_parts = uri[len("gs://"):].split('/', 1)
                if len(path_parts) == 2:
                    bucket_name = path_parts[0]
                    blob_name = path_parts[1]
                    signed_url = generate_download_signed_url_v4(bucket_name, blob_name)
                else:
                    print(f"Warning: Could not parse bucket and blob from URI: {uri}")
            except Exception as e:
                print(f"Error generating signed URL for {uri}: {e}")
                signed_url = "#" # Fallback to no link on error

        cards_html += f"""
        <div class="adk-source-card">
            <div class="adk-source-card-content">{text_content}</div>
            <div class="adk-source-card-footer">
                <a href="{signed_url}" target="_blank" class="adk-source-card-link" title="{title}">{title}</a>
            </div>
        </div>
        """

    return f"""
    <details class="sources-details" open>
        <summary>Sources</summary>
        <div class="sources-panel-container">
            <div class="adk-sources-container">{cards_html}</div>
        </div>
    </details>
    """

# --- CORRECTED FUNCTION ---
async def chat_with_agent(message, history):
    """
    Core function. Takes user message and history, returns ONLY the
    assistant's response string. Gradio handles the history updates.
    """
    global session, session_id
    if session is None or session_id is None:
        session = await session_service.create_session(app_name="GroupamaAgent", user_id=user_id)
        session_id = session.id

    assistant_response_parts = []
    sources_html = ""
        
    content = types.Content(role="user", parts=[types.Part(text=message)])

    response = []
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if (hasattr(event, 'actions') and event.actions and
            hasattr(event.actions, 'state_delta') and event.actions.state_delta and
            'last_grounding_metadata' in event.actions.state_delta and
            event.actions.state_delta['last_grounding_metadata']):
            
            grounding_metadata = event.actions.state_delta['last_grounding_metadata']
            sources_html = create_sources_html(grounding_metadata)

        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    assistant_response_parts.append(part.text)

    final_response_text = "".join(assistant_response_parts)
    
    # Combine the text and the sources HTML into a single string.
    response.append(final_response_text)
    response.append(gr.HTML(sources_html))
    
    # Return ONLY the assistant's response string.
    return response

demo = gr.ChatInterface(
    chat_with_agent,
    examples=["Am inclus RMN in asigurarea medicala?"],
    css=CUSTOM_CSS,
    chatbot= gr.Chatbot(
        scale=1,
        elem_id="chatbot",
        ),
)

if __name__ == "__main__":
    demo.launch()