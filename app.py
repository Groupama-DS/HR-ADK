import gradio as gr
import os
from agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.genai import types
import re
from google.adk.agents.run_config import RunConfig
from google.adk.agents.run_config import StreamingMode

from app_utils import CUSTOM_CSS, generate_download_signed_url_v4, CustomChatInterface

# Bypass the system proxy for localhost communication.
os.environ['NO_PROXY'] = '127.0.0.1,localhost'
session_service = InMemorySessionService()
runner = Runner(
    app_name="GroupamaAgent",
    agent=root_agent,
    session_service=session_service,
)
user_id = "demo_user"
session = None
session_id = None

def create_sources_markdown(grounding_metadata):
    """
    Creates a Markdown formatted string for the sources.
    """
    if not grounding_metadata or not hasattr(grounding_metadata, 'grounding_chunks') or not grounding_metadata.grounding_chunks:
        return ""

    used_chunk_indices = set()
    if grounding_metadata and grounding_metadata.grounding_supports:
        for support in grounding_metadata.grounding_supports:
            for chunk_idx in support.grounding_chunk_indices:
                used_chunk_indices.add(chunk_idx)

    if not used_chunk_indices:
        return ""

    markdown_parts = []
    for i, chunk in enumerate(grounding_metadata.grounding_chunks):
        if i in used_chunk_indices:
            retrieved_context = chunk.retrieved_context
            title = getattr(retrieved_context, 'title', 'Source Document')
            uri = getattr(retrieved_context, 'uri', '#')
            text_content = getattr(retrieved_context, 'text', 'No content available.')
            
            signed_url = "#"
            if uri.startswith("gs://"):
                try:
                    path_parts = uri[len("gs://"):].split('/', 1)
                    if len(path_parts) == 2:
                        bucket_name, blob_name = path_parts
                        signed_url = generate_download_signed_url_v4(bucket_name, blob_name)
                except Exception as e:
                    print(f"Error generating signed URL for {uri}: {e}")
            
            # Format as a Markdown list item with a link and a blockquote for the content
            markdown_parts.append(f"\n1. **[{title}]({signed_url})**")

    if len(markdown_parts) <= 1:
        return ""
    
    sources_md="\n" + "\n".join(markdown_parts)
    full_md = f"<details><summary>Sources</summary>{sources_md}</details>"    
    return full_md


def create_thoughts_markdown(thoughts, is_final=False):
    """
    Creates a Markdown formatted string for the thoughts.
    """
    if not thoughts:
        return ""
    
    full_text_content = "".join(thoughts).strip()
    if not full_text_content:
        return ""
        
    individual_thoughts = re.split(r'\n{2,}(?=\*\*)', full_text_content)
    individual_thoughts = [thought.strip() for thought in individual_thoughts if thought.strip()]
    individual_thoughts = [thought.replace("**\n", "**  ") for thought in individual_thoughts]
    #TODO check individual thoughts to see why sometimes there are double new line displayed

    if not individual_thoughts:
        return ""

    if is_final:
        # Final thoughts are presented clearly under a heading
        thoughts_content_md = "\n\n" + "\n\n".join(individual_thoughts)
        full_md = f"<details><summary>Model Thoughts</summary>{thoughts_content_md}</details>"
        return full_md
    else:
        # Streaming thoughts show the last thought in a blockquote
        last_thought_md = "\n\n" + individual_thoughts[-1]
        full_md = f"<details open><summary>Model Thoughts</summary>{last_thought_md}</details>"
        return full_md


async def chat_with_agent(message, history):
    """
    Handles chat by yielding a single Markdown string for Gradio to render.
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
        user_id=user_id, session_id=session_id, new_message=content,
        run_config=RunConfig(streaming_mode=StreamingMode.SSE, response_modalities=["TEXT"])
    ):
        with open("output.txt", "a", encoding="utf-8") as f:
            f.write(str(event) + "\n##################################################################\n")
            
        if event.is_final_response():
            thought_parts.clear()
            assistant_response_parts.clear()
            
        if event.grounding_metadata and event.grounding_metadata.grounding_chunks:
            grounding_metadata = event.grounding_metadata
            
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, 'thought', False):
                    thought_parts.append(part.text)
                elif hasattr(part, 'text') and part.text:
                    assistant_response_parts.append(part.text)

            thoughts_md = create_thoughts_markdown(thought_parts, is_final=False)
            response_so_far = "".join(assistant_response_parts)

            # --- KEY CHANGE (STREAMING) ---
            # Yield a combined Markdown string.
            yield f"{thoughts_md}\n\n{response_so_far}"

    # --- Combine all parts for the final output ---
    final_response_text = "".join(assistant_response_parts)
    sources_md = create_sources_markdown(grounding_metadata)
    final_thoughts_md = create_thoughts_markdown(thought_parts, is_final=True)
    yield f"{final_thoughts_md}\n\n{final_response_text}\n\n{sources_md}"


with gr.Blocks(fill_height=True, fill_width=True, css=CUSTOM_CSS) as demo:
    def handle_like(data: gr.LikeData):
        print(f"Feedback Received:")
        # TODO feedback to big query

    # The standard gr.Chatbot component is sufficient now.
    chatbot = gr.Chatbot(
        elem_id="chatbot",
        type="messages",
        render_markdown=True,
        # sanitize_html is True by default, which is safer now that we don't need custom HTML.
    )
    chatbot.like(handle_like, None, None)

    # Use the standard gr.ChatInterface
    gr.ChatInterface(
        chat_with_agent,
        type="messages",
        examples=["Am inclus RMN in asigurarea medicala?", "Ce beneficii am ca angajat?"],
        save_history=True,
        flagging_mode="manual",
        chatbot=chatbot,
    )

if __name__ == "__main__":
    demo.launch()