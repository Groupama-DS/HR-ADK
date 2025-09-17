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
        if any(isinstance(h, google.cloud.logging.handlers.CloudLoggingHandler) for h in logging.root.handlers):
             print("Cloud Logging handler already attached.")
             _logging_configured = True
             return

        # Retrieves a Cloud Logging handler and integrates it with Python's logging module.
        client.setup_logging()
        
        log_name = "groupama-agent-chat"
        print("Cloud Logging successfully set up.")
        
    except Exception as e:
        print(f"Could not set up Cloud Logging: {e}. Falling back to standard output logging.")
        logging.basicConfig(level=logging.INFO)
        log_name = "local-logger"
    
    _logging_configured = True

setup_cloud_logging()

session_service = InMemorySessionService()
runner = Runner(
    app_name="GroupamaAgent",
    agent=root_agent,
    session_service=session_service,
)
user_id = "demo_user"

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

    if not individual_thoughts:
        return ""

    if is_final:
        thoughts_content_md = "\n\n" + "\n\n".join(individual_thoughts)
        full_md = f"<details><summary>Proces de Gândire</summary>{thoughts_content_md}</details>"
        return full_md
    else:
        last_thought_md = "\n\n" + individual_thoughts[-1]
        full_md = f"<details open><summary>Proces de Gândire</summary>{last_thought_md}</details>"
        return full_md


async def chat_with_agent(message, history, active_session_id):
    """
    Handles chat by yielding a single Markdown string for Gradio to render.
    """
    if not history or active_session_id is None:
        session = await session_service.create_session(app_name="GroupamaAgent", user_id=user_id)
        active_session_id = session.id
        print(f"New session: {active_session_id}")

    assistant_response_parts = []
    thought_parts = []
    grounding_metadata = None

    content = types.Content(role="user", parts=[types.Part(text=message)])
    async for event in runner.run_async(
        user_id=user_id, session_id=active_session_id, new_message=content,
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

    message_id = len(history) + 1

    final_response_text = "".join(assistant_response_parts)
    sources_md = create_sources_markdown(grounding_metadata)
    final_thoughts_md = create_thoughts_markdown(thought_parts, is_final=True)
    # IMPORTANT: We append the session ID to the response content so we can retrieve it later
    response = f"{final_thoughts_md}\n\n{final_response_text}\n\n{sources_md}\n\n{active_session_id}"
    
    log_data = {
        "message_id": message_id,
        "session_id": active_session_id,
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
        "liked": None,
        "dislike_reason": None,
    }
    logging.info(f"Conversation log: {message_id}/{active_session_id}/{user_id}", extra={'json_fields': log_data})

    return response, active_session_id

# --- MODIFIED: This function is no longer needed as a separate function ---
# def handle_like(data: gr.LikeData, history):
#     ...

with gr.Blocks(fill_height=True, fill_width=True, css=CUSTOM_CSS, title="Hr Chatbot") as demo:
    active_session_state = gr.State(None)
    chatbot = gr.Chatbot(
        elem_id="chatbot",
        type="messages",
        render_markdown=True,
    )

    with gr.Group(elem_id="dislike_overlay", visible=False) as dislike_modal:
        with gr.Column():
            dislike_reason_box = gr.Textbox(
                label="Ce este gresit?",
                lines=3,
                placeholder="Enter your reason here...",
            )
            submit_reason_btn = gr.Button("Submit Reason")

    like_data_state = gr.State(None)

    gr.ChatInterface(
        chat_with_agent,
        type="messages",
        examples=[["Am inclus RMN in asigurarea medicala?", None], ["Ce beneficii am ca angajat?", None]],
        save_history=True,
        flagging_mode="manual",
        chatbot=chatbot,
        additional_inputs=[active_session_state],
        additional_outputs=[active_session_state],
    )

    # --- NEW FUNCTION TO HANDLE HISTORY LOADING ---
    def update_session_on_history_load(history):
        """
        Parses the loaded chat history to find the session ID from the last assistant message.
        """
        if not history:
            return None  # It's a new or cleared chat

        last_assistant_message_content = None
        # Iterate backwards through history to find the last message from the assistant
        for message in reversed(history):
            if message.get("role") == "assistant":
                last_assistant_message_content = message.get("content")
                break

        if not last_assistant_message_content:
            return None # No assistant message found, might be a new chat

        # Use regex to find a UUID-like string at the very end of the content
        match = re.search(r'([a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12})\s*$', last_assistant_message_content, re.IGNORECASE)
        
        if match:
            session_id = match.group(1)
            print(f"History loaded. Switching to ADK session: {session_id}")
            return session_id
        else:
            print("Could not find a valid session ID in the last message.")
            return None # Fallback to creating a new session

    # --- NEW EVENT LISTENER ---
    # This event updates the session state whenever the chatbot's value changes
    # (e.g., when a saved conversation is loaded).
    chatbot.change(
        fn=update_session_on_history_load,
        inputs=[chatbot],
        outputs=[active_session_state],
        queue=False # This can run outside the queue for responsiveness
    )

    # --- MODIFIED: on_like function now accepts session state ---
    def on_like(data: gr.LikeData, history, current_session_id):
        if data.liked is False:
            return gr.update(visible=True), data
        else:
            # If liked, log it immediately and ensure the overlay is hidden
            log_data = {
                "message_id": data.index + 1,
                "session_id": current_session_id,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "log_type": "feedback",
                "question": history[data.index][0],
                "answer": history[data.index][1],
                "liked": data.liked,
                "dislike_reason": None,
            }
            logging.info(f"Feedback log: {log_data['message_id']}/{current_session_id}/{user_id}", extra={'json_fields': log_data})
            return gr.update(visible=False), None

    # --- MODIFIED: .like() event now passes session state as input ---
    chatbot.like(
        on_like,
        inputs=[chatbot, active_session_state],
        outputs=[dislike_modal, like_data_state],
    )

    # --- MODIFIED: on_submit_reason function now accepts session state ---
    def on_submit_reason(reason, data, history, current_session_id):
        log_data = {
            "message_id": data.index + 1,
            "session_id": current_session_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "log_type": "feedback",
            "question": history[data.index][0],
            "answer": history[data.index][1],
            "liked": False,
            "dislike_reason": reason,
        }
        logging.info(f"Feedback log: {log_data['message_id']}/{current_session_id}/{user_id}", extra={'json_fields': log_data})
        return gr.update(visible=False), gr.update(value="")

    # --- MODIFIED: .click() event now passes session state as input ---
    submit_reason_btn.click(
        on_submit_reason,
        inputs=[dislike_reason_box, like_data_state, chatbot, active_session_state],
        outputs=[dislike_modal, dislike_reason_box],
    )

if __name__ == "__main__":
    if os.environ.get("ENV") == "dev":
        demo.launch()
    else:
        demo.launch(server_name="0.0.0.0", server_port=8080)