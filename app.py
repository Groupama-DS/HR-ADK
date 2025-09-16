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
from app_utils import CUSTOM_CSS, generate_download_signed_url_v4
from dotenv import load_dotenv
load_dotenv()

if os.environ.get("ENV") == "dev":
    os.environ['NO_PROXY'] = '127.0.0.1,localhost'

# TODO list:
# instance always up
# translate app (there are english words)
# 

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
    else:
        # If there are no grounding_supports, use all grounding_chunks
        used_chunk_indices = set(range(len(grounding_metadata.grounding_chunks)))

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

    if len(markdown_parts) == 0:
        return ""
    
    sources_md="\n" + "\n".join(markdown_parts)
    full_md = f"<details><summary>Surse</summary>{sources_md}</details>"    
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
        full_md = f"<details><summary>Proces de Gândire</summary>{thoughts_content_md}</details>"
        return full_md
    else:
        # Streaming thoughts show the last thought in a blockquote
        last_thought_md = "\n\n" + individual_thoughts[-1]
        full_md = f"<details open><summary>Proces de Gândire</summary>{last_thought_md}</details>"
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
        run_config=RunConfig(streaming_mode=StreamingMode.NONE, response_modalities=["TEXT"])
    ):
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
            "role": "user"
        },
        "answer": {
            "content": response,
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



with gr.Blocks(fill_height=True, fill_width=True, css=CUSTOM_CSS, title="Hr Chatbot") as demo:
    chatbot = gr.Chatbot(
        elem_id="chatbot",
        type="messages",
        render_markdown=True,
    )

    # --- CHANGE 1: Wrap dislike components in a styled, invisible group ---
    # This group will act as our modal overlay.
    with gr.Group(elem_id="dislike_overlay", visible=False) as dislike_modal:
        with gr.Column():
            dislike_reason_box = gr.Textbox(
                label="Ce este gresit?",
                lines=3,
                placeholder="Enter your reason here...",
                # No need to set visible=False here, the parent group handles it
            )
            submit_reason_btn = gr.Button("Submit Reason")

    # This remains the same
    like_data_state = gr.State(None)

    gr.ChatInterface(
        chat_with_agent,
        type="messages",
        examples=["Am inclus RMN in asigurarea medicala?", "Ce beneficii am ca angajat?"],
        save_history=True,
        flagging_mode="manual",
        chatbot=chatbot,
    )

    # --- CHANGE 2: Modify the on_like function to control the new overlay ---
    def on_like(data: gr.LikeData, history):
        if data.liked is False:
            # When disliked, show the entire modal overlay and store the LikeData
            return gr.update(visible=True), data
        else:
            # If liked, log it immediately and ensure the overlay is hidden
            handle_like(data, history)
            return gr.update(visible=False), None

    # --- CHANGE 3: Update the .like() event to target the new overlay ---
    chatbot.like(
        on_like,
        inputs=[chatbot],
        outputs=[dislike_modal, like_data_state], # Target the group, not individual components
    )

    # --- CHANGE 4: Modify the on_submit_reason function and its trigger ---
    def on_submit_reason(reason, data, history):
        # 'data' now correctly refers to the gr.LikeData object stored in the state
        log_data = {
            # Gradio LikeData is 0-indexed, so we add 1 for a message ID
            "message_id": data.index + 1,
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "log_type": "feedback",
            # The history format is [[user_msg, bot_msg], ...].
            # data.index points to the correct pair.
            "question": history[data.index - 1],
            "answer": history[data.index],
            "liked": False,
            "dislike_reason": reason,
        }
        logging.info(f"Feedback log: {log_data['message_id']}/{session_id}/{user_id}", extra={'json_fields': log_data})
        # Hide the modal and clear the textbox after submission
        return gr.update(visible=False), gr.update(value="")

    submit_reason_btn.click(
        on_submit_reason,
        # Pass the reason from the textbox, the data from the state, and the history
        inputs=[dislike_reason_box, like_data_state, chatbot],
        # Update the modal to be invisible and clear the textbox
        outputs=[dislike_modal, dislike_reason_box],
    )

if __name__ == "__main__":
    if os.environ.get("ENV") == "dev":
        demo.launch()
    else:
        demo.launch(server_name="0.0.0.0", server_port=8080)