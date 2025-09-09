import gradio as gr
import os
from agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.genai import types
import re
from google.adk.agents.run_config import RunConfig
from google.adk.agents.run_config import StreamingMode
import google.cloud.logging
import logging
import uuid
from datetime import datetime, timezone
from app_utils import CUSTOM_CSS, generate_download_signed_url_v4, CustomChatInterface

_logging_configured = False

def setup_cloud_logging():
    """Initializes Cloud Logging safely, preventing duplicate handlers."""
    global _logging_configured
    if _logging_configured:
        return

    try:
        # Instantiate a client
        client = google.cloud.logging.Client()
        
        # Check if a handler of this type is already attached to the root logger
        # This is an even more robust check than a simple flag.
        if any(isinstance(h, google.cloud.logging.handlers.CloudLoggingHandler) for h in logging.root.handlers):
             print("Cloud Logging handler already attached.")
             _logging_configured = True
             return

        # Retrieves a Cloud Logging handler and integrates it with Python's logging module.
        client.setup_logging()
        
        # The name for your logger
        log_name = "groupama-agent-chat"
        print("Cloud Logging successfully set up.")
        
    except Exception as e:
        print(f"Could not set up Cloud Logging: {e}. Falling back to standard output logging.")
        # Fallback to basic logging if Cloud Logging fails to initialize
        logging.basicConfig(level=logging.INFO)
        log_name = "local-logger"
    
    _logging_configured = True

# --- Call the setup function ---
setup_cloud_logging()

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
            # yield f"{thoughts_md}\n\n{response_so_far}"

    message_id = len(history) + 1

    # --- Combine all parts for the final output ---
    final_response_text = "".join(assistant_response_parts)
    sources_md = create_sources_markdown(grounding_metadata)
    final_thoughts_md = create_thoughts_markdown(thought_parts, is_final=True)
    response = f"{final_thoughts_md}\n\n{final_response_text}\n\n{sources_md}"
    
    log_data = {
        "message_id": message_id,
        "session_id": session_id,
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "log_type": "conversation",
        "question": {
            "content": message,
            "metadata": None,
            "options": None,
            "role": "user"
        },
        "answer": {
            "content": response,
            "metadata": None,
            "options": None,
            "role": "assistant"
        },
        "liked": None,  # The initial state is "none"
        "dislike_reason": None,
    }
    # Use the `extra` parameter to pass structured data to the Cloud Logging handler
    logging.info(f"Conversation log: {message_id}/{session_id}/{user_id}", extra={'json_fields': log_data})

    return response

def handle_like(data: gr.LikeData, history):
    """
    Handles like/dislike feedback and logs it.
    """
    log_data = {
        "message_id": data.index,
        "session_id": session_id,
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "log_type": "feedback",
        "question": history[data.index - 1],
        "answer": history[data.index],
        "liked": data.liked,
        "dislike_reason": None, # You can add a mechanism to collect this if needed
    }
    logging.info(f"Feedback log: {log_data['message_id']}/{session_id}/{user_id}", extra={'json_fields': log_data})


with gr.Blocks(fill_height=True, fill_width=True, css=CUSTOM_CSS) as demo:

    # The standard gr.Chatbot component is sufficient now.
    chatbot = gr.Chatbot(
        elem_id="chatbot",
        type="messages",
        render_markdown=True,
        # sanitize_html is True by default, which is safer now that we don't need custom HTML.
    )
    chatbot.like(handle_like, inputs=[chatbot], outputs=None)

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