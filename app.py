import gradio as gr
import os
from agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

# Bypass the system proxy for localhost communication.
os.environ['NO_PROXY'] = '127.0.0.1,localhost'

# --- 1. Define Advanced CSS for Layout and Theming ---
CUSTOM_CSS = """

footer {
    visibility: hidden
}
/* === Page Layout: Make the app fill the viewport without scrolling === */
html, body {
    height: 100%;
    overflow: hidden; /* Prevent main page scroll */
    margin: 0;
    padding: 0;
}
#root { /* Gradio's main container */
    height: 100vh;
    display: flex;
    flex-direction: column;
}
.chat-container { /* A new class for our main content area */
    flex-grow: 1; /* This makes the column take all available vertical space */
    overflow: hidden; /* Hide overflow from this container */
    display: flex;
    flex-direction: column;
}
.gradio-chat {
    flex-grow: 1; /* Make the chatbot component itself grow */
    overflow-y: auto; /* Ensure scrolling happens *inside* the chatbot */
}

/* === Collapsible Sources Styling === */
details.sources-details {
    border: 1px solid var(--border-color-primary);
    border-radius: var(--radius-lg);
    margin-top: 10px;
}
details.sources-details summary {
    cursor: pointer;
    padding: 10px;
    font-weight: bold;
    color: var(--text-color-secondary);
    background: var(--background-fill-secondary);
    border-radius: var(--radius-lg);
}
details.sources-details[open] summary { /* Style when open */
    border-bottom: 1px solid var(--border-color-primary);
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
}
details.sources-details:hover {
    border-color: var(--color-accent);
}

/* === Source Card Styling (Theme-Aware) === */
.sources-panel-container {
    padding: 10px;
}
.adk-sources-container {
    display: flex;
    overflow-x: auto;
    gap: 16px;
    padding-bottom: 10px;
}
.adk-source-card {
    flex: 0 0 300px;
    width: 300px;
    height: 200px;
    border: 1px solid var(--border-color-primary);
    border-radius: var(--radius-lg);
    padding: 12px;
    background: var(--background-fill-primary);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    font-family: var(--font);
    font-size: var(--text-sm);
    color: var(--text-color-primary);
}
.adk-source-card-content { overflow-y: auto; flex-grow: 1; }
.adk-source-card-footer { margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--border-color-primary); }
.adk-source-card-title { font-weight: bold; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--text-color-primary); }
.adk-source-card-link { color: var(--color-accent); text-decoration: none; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.adk-source-card-link:hover { text-decoration: underline; }
"""

# Set up session service and runner
session_service = InMemorySessionService()
runner = Runner(
    app_name="GroupamaAgent",
    agent=root_agent,
    session_service=session_service,
)

def create_sources_html(grounding_metadata):
    """Generates the HTML for the source cards, wrapped in a collapsible <details> tag."""
    # --- 3. Return an empty string to be completely invisible ---
    if not grounding_metadata or 'grounding_chunks' not in grounding_metadata or not grounding_metadata['grounding_chunks']:
        return ""

    cards_html = ""
    for chunk in grounding_metadata['grounding_chunks']:
        retrieved_context = chunk.get('retrieved_context', {})
        title = retrieved_context.get('title', 'Source Document')
        uri = retrieved_context.get('uri', '#')
        text_content = retrieved_context.get('text', 'No content available.')

        cards_html += f"""
        <div class="adk-source-card">
            <div class="adk-source-card-content">{text_content}</div>
            <div class="adk-source-card-footer">
                <span class="adk-source-card-title" title="{title}">{title}</span>
                <a href="{uri}" target="_blank" class="adk-source-card-link" title="{uri}">{uri}</a>
            </div>
        </div>
        """
    
    # --- 2. Wrap the output in a <details> element, open by default ---
    return f"""
    <details class="sources-details" open>
        <summary>Sources</summary>
        <div class="sources-panel-container">
            <div class="adk-sources-container">{cards_html}</div>
        </div>
    </details>
    """

async def chat_with_agent(user_input, chat_history, session_id):
    """Core function. Returns updated chat history and the separate HTML for sources."""
    user_id = "demo_user"
    
    chat_history.append([user_input, ""])
    assistant_response_parts = []
    sources_html = "" # Default to completely empty

    if not session_id:
        session = await session_service.create_session(app_name="GroupamaAgent", user_id=user_id)
        session_id = session.id
        
    content = types.Content(role="user", parts=[types.Part(text=user_input)])
    
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
    chat_history[-1][1] = final_response_text
    
    return chat_history, session_id, sources_html

async def respond(user_input, chat_history, session_id):
    """Gradio response function. Updates the chatbot, the HTML sources panel, and clears the input box."""
    new_chat_history, new_session_id, final_sources_html = await chat_with_agent(user_input, chat_history, session_id)
    return new_chat_history, new_session_id, final_sources_html, ""

with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Default()) as demo:
    gr.Markdown("# Chat with Groupama Agent")
    session_id_state = gr.State(value=None)
    
    # --- 1. Restructure the layout with a growing Column ---
    with gr.Column(elem_classes=["chat-container"]):
        chatbot = gr.Chatbot(
            label="Conversation",
            bubble_full_width=False,
            elem_classes=["gradio-chat"] # Apply class for CSS targeting
        )
        sources_display = gr.HTML("") # Start with empty HTML

    with gr.Row():
        msg = gr.Textbox(
            label="Your Message",
            placeholder="Type your message here and press Enter...",
            scale=4 # Give textbox more width
        )

    msg.submit(
        fn=respond,
        inputs=[msg, chatbot, session_id_state],
        outputs=[chatbot, session_id_state, sources_display, msg]
    )

if __name__ == "__main__":
    demo.launch()