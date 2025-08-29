import gradio as gr
import os
from agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import html

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
    if not grounding_metadata or not hasattr(grounding_metadata, 'grounding_chunks') or not grounding_metadata.grounding_chunks:
        return ""
    
    used_chunk_indices = set()
    if grounding_metadata and grounding_metadata.grounding_supports:
        # Collect all unique chunk indices that were used
        for support in grounding_metadata.grounding_supports:
            for chunk_idx in support.grounding_chunk_indices:
                used_chunk_indices.add(chunk_idx + 1)

    cards_html = ""
    # Use enumerate to get a numbered index for each source, starting from 1
    for i, chunk in enumerate(grounding_metadata.grounding_chunks, 1):
        if i in used_chunk_indices:
            retrieved_context = chunk.retrieved_context
            title = getattr(retrieved_context, 'title', 'Source Document')
            uri = getattr(retrieved_context, 'uri', '#')
            text_content = getattr(retrieved_context, 'text', 'No content available.')

            # Escape HTML special characters in the text content to prevent XSS
            escaped_text_content = html.escape(text_content)

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
                <div class="adk-source-card-content">{escaped_text_content}</div>
                <div class="adk-source-card-footer">
                    <a href="{signed_url}" target="_blank" class="adk-source-card-link" title="{title}"><strong>{i}.</strong> {title}</a>
                </div>
            </div>
            """

    return f"""
    <details class="sources-details">
        <summary>Sources</summary>
        <div class="sources-panel-container">
            <div class="adk-sources-container">{cards_html}</div>
        </div>
    </details>
    """

# --- MODIFIED FUNCTION 2 ---
async def chat_with_agent(message, history):
    global session, session_id
    if session is None or session_id is None:
        session = await session_service.create_session(app_name="GroupamaAgent", user_id=user_id)
        session_id = session.id

    assistant_response_parts = []
    grounding_metadata = None
    
    # Initialize the full response string that will be updated and yielded
    full_response_so_far = "" 

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
                    new_text_chunk = part.text
                    assistant_response_parts.append(new_text_chunk)
                    full_response_so_far += new_text_chunk
                    # Yield the current full response as it builds
                    print(full_response_so_far)
                    yield full_response_so_far # Yield text and no sources yet

    # After the loop, the full response text is assembled.
    # Now, generate the sources and yield the final response with sources.
    final_response_text = "".join(assistant_response_parts)
    sources_html = create_sources_html(grounding_metadata)

    yield [final_response_text, gr.HTML(sources_html)] # Final yield with sources


demo = gr.ChatInterface(
    chat_with_agent,
    examples=["Am inclus RMN in asigurarea medicala?", "Ce beneficii am ca angajat?"],
    css=CUSTOM_CSS,
    chatbot= gr.Chatbot(
        scale=1,
        elem_id="chatbot",
        ),
)

if __name__ == "__main__":
    demo.launch()