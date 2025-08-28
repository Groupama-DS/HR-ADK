import gradio as gr
import os
from agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json
import pprint

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

# --- MODIFIED FUNCTION 1 ---
def create_sources_html(grounding_metadata):
    """
    Generates the HTML for the numbered source cards, wrapped in a
    collapsible <details> tag.
    """
    if not grounding_metadata or 'grounding_chunks' not in grounding_metadata or not grounding_metadata['grounding_chunks']:
        return ""

    cards_html = ""
    # Use enumerate to get a numbered index for each source, starting from 1
    for i, chunk in enumerate(grounding_metadata['grounding_chunks'], 1):
        retrieved_context = chunk.get('retrieved_context', {})
        title = retrieved_context.get('title', 'Source Document')
        uri = retrieved_context.get('uri', '#')
        text_content = retrieved_context.get('text', 'No content available.')

        # Extract bucket and blob name from gs:// URI
        signed_url = "#"
        if uri.startswith("gs://"):
            try:
                path_parts = uri[len("gs://"):].split('/', 1)
                if len(path_parts) == 2:
                    bucket_name = path_parts[0]
                    blob_name = path_parts[1]
                    signed_url = generate_download_signed_url_v4(bucket_name, blob_name)
                else:
                    print(f"Warning: Could not parse bucket and blob from URI: {uri}")
            except Exception as e:
                print(f"Error generating signed URL for {uri}: {e}")
                signed_url = "#"

        # Add the citation number (i) to the card's footer
        cards_html += f"""
        <div class="adk-source-card">
            <div class="adk-source-card-content">{text_content}</div>
            <div class="adk-source-card-footer">
                <a href="{signed_url}" target="_blank" class="adk-source-card-link" title="{title}"><strong>{i}.</strong> {title}</a>
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

# --- MODIFIED FUNCTION 2 ---
async def chat_with_agent(message, history):
    """
    Core function. Takes user message and history, returns the assistant's
    response with inline citations and the sources HTML.
    """
    global session, session_id
    if session is None or session_id is None:
        session = await session_service.create_session(app_name="GroupamaAgent", user_id=user_id)
        session_id = session.id

    assistant_response_parts = []
    grounding_metadata = None # Initialize to store the metadata

    content = types.Content(role="user", parts=[types.Part(text=message)])

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            grounding_metadata = event.grounding_metadata
            
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    assistant_response_parts.append(part.text)

        print(event)

    final_response_text = "".join(assistant_response_parts)

    # --- NEW CITATION INSERTION LOGIC ---
    if grounding_metadata and 'grounding_supports' in grounding_metadata:
        # Sort supports by end_index in descending order to avoid index shifting issues
        supports = sorted(
            grounding_metadata['grounding_supports'],
            key=lambda x: x['segment']['end_index'],
            reverse=True
        )

        for support in supports:
            end_index = support['segment']['end_index']
            # Create citation string like "[1]" or "[1, 2]"
            # Adding 1 to each index to match the 1-based numbering of the cards
            citation_indices = [str(i + 1) for i in support['grounding_chunk_indices']]
            citation_text = f" [{', '.join(citation_indices)}]"

            # Insert the citation text into the final response
            final_response_text = final_response_text[:end_index] + citation_text + final_response_text[end_index:]
    # --- END OF NEW LOGIC ---

    # Generate the numbered sources HTML
    sources_html = create_sources_html(grounding_metadata)

    # Return the text with citations and the sources component
    return [final_response_text, gr.HTML(sources_html)]


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