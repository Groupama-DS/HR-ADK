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

ENV = os.environ.get("ENV")
if os.environ.get("DEBUG") == "True":
    DEBUG = True
else:
    DEBUG = False



if ENV == "local":
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
        client = google.cloud.logging.Client()
        if any(isinstance(h, google.cloud.logging.handlers.CloudLoggingHandler) for h in logging.root.handlers):
             logging.info("Cloud Logging handler already attached.")
             _logging_configured = True
             return
        client.setup_logging()
        log_name = "groupama-agent-chat"
        logging.info("Cloud Logging successfully set up.")
        
    except Exception as e:
        logging.error(f"Could not set up Cloud Logging: {e}. Falling back to standard output logging.")
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
    """Creates a Markdown formatted string for the sources."""
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
                    logging.error(f"Error generating signed URL for {uri}: %s", e)
            
            markdown_parts.append(f"\n1. **[{title}]({signed_url})**")

    if len(markdown_parts) == 0:
        return ""
    
    sources_md = "\n" + "\n".join(markdown_parts)
    full_md = f"<details><summary>Surse</summary>{sources_md}</details>"    
    return full_md

def create_thoughts_markdown(thoughts, is_final=False):
    """Creates a Markdown formatted string for the thoughts."""
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
        thoughts_content_md = "\n\n" + "\n\n".join(individual_thoughts)
        full_md = f"<details><summary>Proces de Gândire</summary>{thoughts_content_md}</details>"
        return full_md
    else:
        last_thought_md = "\n\n" + individual_thoughts[-1]
        full_md = f"<details open><summary>Proces de Gândire</summary>{last_thought_md}</details>"
        return full_md

async def chat_with_agent(message, history, active_session_id, session_history):
    """
    Handles chat, managing the active_session_id and the list of historical session IDs.
    """
    is_new_conversation = len(history) <= 1

    if is_new_conversation:
        session = await session_service.create_session(app_name="GroupamaAgent", user_id=user_id)
        active_session_id = session.id
        logging.info(f"New session created: {active_session_id}")
        session_history.insert(0, active_session_id)
    else:
        # This can happen if the user clicks an old chat without a corresponding session in our history
        if not active_session_id:
            logging.warning("No active session ID found for existing chat. Creating a new one.")
            session = await session_service.create_session(app_name="GroupamaAgent", user_id=user_id)
            active_session_id = session.id
            session_history.insert(0, active_session_id) # Or you might want to handle this differently
        else:
            logging.info(f"Continuing session: {active_session_id}")

    assistant_response_parts = []
    thought_parts = []
    grounding_metadata = None

    content = types.Content(role="user", parts=[types.Part(text=message)])
    async for event in runner.run_async(
        user_id=user_id, session_id=active_session_id, new_message=content,
        run_config=RunConfig(streaming_mode=StreamingMode.NONE, response_modalities=["TEXT"])
    ):
        if ENV == "local":
            with open("output.txt", "a") as f:
                f.write(f"Event: {event}\n")

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
    final_response_text = "".join(assistant_response_parts)
    sources_md = create_sources_markdown(grounding_metadata)
    final_thoughts_md = create_thoughts_markdown(thought_parts, is_final=True)
    response = f"{final_thoughts_md}\n\n{final_response_text}\n\n{sources_md}"
    if DEBUG == True:
        response += f"\n\n{active_session_id}"
    
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
        "liked": None,  # The initial state is "none"
        "dislike_reason": None,
    }
    logging.info(f"Conversation log: {message_id}/{active_session_id}/{user_id}", extra={'json_fields': log_data})

    return response, active_session_id, session_history

with gr.Blocks(fill_height=True, fill_width=True, css=CUSTOM_CSS, title="Hr Chatbot") as demo:
    active_session_state = gr.State(None)
    session_history_state = gr.BrowserState([], storage_key="adk_session_history")

    chatbot = gr.Chatbot(
        elem_id="chatbot",
        type="messages",
        render_markdown=True,
    )

    with gr.Group(elem_id="dislike_overlay", visible=False) as dislike_modal:
        with gr.Column():
            dislike_reason_box = gr.Textbox(
                label="Ce este greșit?",
                lines=5,
                placeholder="Te rog să spui care este răspunsul corect și pe ce document se bazează.",
                # No need to set visible=False here, the parent group handles it
            )
            submit_reason_btn = gr.Button("Submit Reason")

    like_data_state = gr.State(None)

    chat_interface = gr.ChatInterface(
        chat_with_agent,
        type="messages",
        examples=[["Am inclus RMN in asigurarea medicala?", None], ["Ce beneficii am ca angajat?", None]],
        save_history=True,
        flagging_mode="manual",
        chatbot=chatbot,
        additional_inputs=[active_session_state, session_history_state],
        additional_outputs=[active_session_state, session_history_state],
    )

    # --- Event Handlers for Session Synchronization ---

    def load_session_from_history(evt: gr.SelectData, session_history: list):
        """When a user clicks a chat in history, retrieve the corresponding session ID."""
        clicked_index = evt.index
        if session_history and 0 <= clicked_index < len(session_history):
            session_id_to_load = session_history[clicked_index]
            logging.info(f"Loading session ID: {session_id_to_load} from history index: {clicked_index}")
            return session_id_to_load
        logging.warning(f"Warning: Could not find session ID for history index {clicked_index}. Starting new session.")
        return None

    chat_interface.chat_history_dataset.select(
        fn=load_session_from_history,
        inputs=[session_history_state],
        outputs=[active_session_state],
        show_progress="hidden", queue=False,
    )

    def start_new_chat():
        """Clears the active session ID when 'New chat' is clicked."""
        logging.info("Starting new chat, clearing active session.")
        return None

    chat_interface.new_chat_button.click(
        fn=start_new_chat, inputs=None, outputs=[active_session_state], queue=False
    )

    def delete_session_from_history(conversation_id_index, session_history):
        """Removes session ID when a conversation is deleted."""
        if conversation_id_index is not None and session_history and 0 <= conversation_id_index < len(session_history):
            logging.info(f"Deleting session ID at index: {conversation_id_index}")
            session_history.pop(conversation_id_index)
        return session_history

    chat_interface.chatbot.clear(
        fn=delete_session_from_history,
        inputs=[chat_interface.conversation_id, session_history_state],
        outputs=[session_history_state], queue=False,
    )

    # --- Updated Feedback Logic ---

    def handle_like(data: gr.LikeData, history, session_id):
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

    def on_like(data: gr.LikeData, history, current_session_id):
        """Handles the like/dislike user action."""
        if not current_session_id:
            logging.error("Error: Could not log feedback because no active session ID was found.")
            return gr.update(visible=False), None # Hide modal and do nothing
        if data.liked is False:
            return gr.update(visible=True), (data, current_session_id)
        else:
            handle_like(data, history, current_session_id)
            return gr.update(visible=False), None

    chatbot.like(
        on_like, inputs=[chatbot, active_session_state], outputs=[dislike_modal, like_data_state]
    )

    def on_submit_reason(reason, like_state_data, history):
        """Handles submission of the dislike reason."""
        if not like_state_data:
            return gr.update(visible=False), gr.update(value="")
            
        data, session_id = like_state_data
        message_id = data.index + 1
        log_data = {
            # Gradio LikeData is 0-indexed, so we add 1 for a message ID
            "message_id": data.index,
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
        return gr.update(visible=False), gr.update(value="")

    submit_reason_btn.click(
        on_submit_reason,
        inputs=[dislike_reason_box, like_data_state, chatbot],
        outputs=[dislike_modal, dislike_reason_box],
    )

if __name__ == "__main__":
    if ENV=="local":
        demo.launch()
    else:
        demo.launch(server_name="0.0.0.0", server_port=8080)