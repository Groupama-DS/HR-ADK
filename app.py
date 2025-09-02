import gradio as gr
import os
from agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import html
import markdown
import re
from google.adk.agents.run_config import RunConfig
from google.adk.agents.run_config import StreamingMode

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

# --- MODIFIED FUNCTION ---
def create_thoughts_html(thoughts, is_final=False):
    """
    Generates an expandable HTML component to display the agent's thoughts.

    If is_final is False (streaming), it shows the last thought in the summary.
    If is_final is True (finished), it shows a static "expand/collapse" message.
    """
    if not thoughts:
        return ""

    # Combine all thought parts for reliable parsing.
    full_text_content = "".join(thoughts).strip()
    if not full_text_content:
        return ""

    # Split into individual thoughts.
    individual_thoughts = re.split(r'\n{2,}(?=\*\*)', full_text_content)
    individual_thoughts = [thought.strip() for thought in individual_thoughts if thought.strip()]
    if not individual_thoughts:
        return ""

    # --- Summary Line Logic ---
    summary_content_html = ""
    if is_final:
        # Final state: show static "expand/collapse" text.
        summary_content_html = """
        <span class="summary-title">
            <span class="expand-text">expand to view model thoughts</span>
            <span class="collapse-text">collapse to hide model thoughts</span>
        </span>
        <span class="summary-chevron"></span>
        """
    else:
        # Streaming state: show the latest thought.
        last_thought = individual_thoughts[-1]
        rendered_last_thought = markdown.markdown(last_thought, extensions=['fenced_code', 'tables'])
        rendered_last_thought = re.sub(r'^<p>|</p>$', '', rendered_last_thought).strip()
        chevron_style = "display: none;" if len(individual_thoughts) <= 1 else ""
        summary_content_html = f"""
        <div class="summary-title">{rendered_last_thought}</div>
        <span class="summary-chevron" style="{chevron_style}"></span>
        """


    # --- Full Panel Content ---
    all_thoughts_html = ""
    for thought in individual_thoughts:
        rendered_thought = markdown.markdown(thought, extensions=['fenced_code', 'tables'])
        all_thoughts_html += f'<div class="thought-item">{rendered_thought}</div>'


    return f"""
    <details class="thoughts-details">
        <summary class="thoughts-summary">
            <div class="summary-top-header">
                <div class="summary-top-left">
                    <span class="sparkle-icon"></span>
                    <span class="thinking-text">Thoughts</span>
                    <span class="loading-dots">
                        <span></span><span></span><span></span>
                    </span>
                </div>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-bottom-line">
                {summary_content_html}
            </div>
        </summary>
        <div class="thoughts-panel-container">
            {all_thoughts_html}
        </div>
    </details>
    """


async def chat_with_agent(message, history):
    """
    Handles the chat interaction, separating thoughts from the main response
    and yielding updates for all UI components.
    """
    global session, session_id
    if session is None or session_id is None:
        session = await session_service.create_session(app_name="GroupamaAgent", user_id=user_id)
        session_id = session.id

    assistant_response_parts = []
    thought_parts = []
    grounding_metadata = None

    content = types.Content(role="user", parts=[types.Part(text=message)])

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
        run_config=RunConfig(
            streaming_mode=StreamingMode.SSE
        )
    ):
        if event.is_final_response():
            thought_parts.clear()
        if event.grounding_metadata:
            if event.grounding_metadata.grounding_chunks:
                grounding_metadata = event.grounding_metadata

        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, 'thought', False):
                    thought_parts.append(part.text)
                elif hasattr(part, 'text') and part.text:
                    assistant_response_parts.append(part.text)

            full_response_so_far = "".join(assistant_response_parts)
            # During streaming, call with is_final=False
            thoughts_html = create_thoughts_html(thought_parts, is_final=False)
            yield [gr.HTML(thoughts_html), full_response_so_far, gr.HTML("")]

    final_response_text = "".join(assistant_response_parts)
    sources_html = create_sources_html(grounding_metadata)
    # After streaming, call with is_final=True for the final static view
    final_thoughts_html = create_thoughts_html(thought_parts, is_final=True)


    yield [gr.HTML(final_thoughts_html), final_response_text, gr.HTML(sources_html)]


demo = gr.ChatInterface(
    chat_with_agent,
    type="messages",
    examples=["Am inclus RMN in asigurarea medicala?", "Ce beneficii am ca angajat?"],
    css=CUSTOM_CSS,
    chatbot= gr.Chatbot(
        scale=1,
        elem_id="chatbot",
        type="messages",
        ),
)

if __name__ == "__main__":
    demo.launch()