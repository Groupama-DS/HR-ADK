import datetime

from google.cloud import storage
import gradio as gr
from gradio import Chatbot
from gradio.components.chatbot import MessageDict
import re

# This helper function remains the same. It identifies your specific HTML output.
def is_my_html_output(content):
    """Checks if a string content is the combined HTML output from the agent."""
    if isinstance(content, str) and (
        '<details class="sources-details">' in content or
        '<details class="thoughts-details">' in content
    ):
        return True
    return False

class CustomChatInterface(gr.ChatInterface):
    def _load_conversation(
        self,
        index: int,
        conversations: list[list[MessageDict]],
    ) -> tuple[int, Chatbot]:
        """
        Overrides the base method to re-hydrate HTML content from saved strings.
        This version correctly handles the conversation data.
        """
        # 1. Get the specific conversation history from the list of saved conversations.
        # This is the raw, serialized data where your HTML is just a string.
        loaded_messages = conversations[index]

        # 2. Iterate through the messages and modify them in place.
        if loaded_messages:
            for i in range(len(loaded_messages)):
                msg = loaded_messages[i]
                # Check if it's an assistant message containing our specific HTML structure.
                if msg.get("role") == "assistant" and is_my_html_output(msg.get("content")):
                    # Replace the raw string with a gr.HTML component object.
                    # This tells Gradio to render it as HTML, not display it as a string.
                    loaded_messages[i]["content"] = gr.HTML(msg["content"])

        # 3. Return a tuple containing the index and a *new* Chatbot component
        #    initialized with our modified conversation history. This perfectly mimics
        #    the behavior and return signature of the original method.
        return (
            index,
            Chatbot(
                value=loaded_messages,  # Pass the modified list here
                feedback_value=[],
                type="messages",
            ),
        )



def generate_download_signed_url_v4(bucket_name, blob_name):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=15),
        # Allow GET requests using this URL.
        method="GET",
    )
    return url





CUSTOM_CSS = """
footer {
    display: none !important;
}

.thoughts-details {
    background-color: var(--body-background-fill);
    border: 1px solid var(--border-color-primary);
    border-radius: var(--radius-lg);
    margin-bottom: 1rem;
    transition: background-color 0.2s ease;
}

/* The entire clickable summary area */
.thoughts-summary {
    display: block;
    padding: 0;
    cursor: pointer;
    outline: none;
    list-style: none; /* Hide default marker in Safari */
}
.thoughts-summary::-webkit-details-marker {
    display: none; /* Hide default marker in Chrome */
}

/* Top header row */
.summary-top-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-lg);
    color: var(--text-color-secondary);
    font-size: var(--text-sm);
}
.summary-top-left {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

/* Sparkle Icon */
.sparkle-icon {
    width: 18px;
    height: 18px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23619aff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 2 L14.5 9.5 L22 12 L14.5 14.5 L12 22 L9.5 14.5 L2 12 L9.5 9.5 Z'/%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
}


.thinking-text {
    color: var(--text-color-primary);
    font-weight: var(--font-weight-semibold);
}

/* Loading Dots Animation */
.loading-dots span {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: var(--text-color-secondary);
    margin: 0 1px;
    animation: loading-pulse 1.4s infinite ease-in-out both;
}
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes loading-pulse {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
    40% { transform: scale(1.0); opacity: 1; }
}

.experimental-text {
    color: var(--text-color-secondary);
}

/* "Auto" button */
.auto-button {
    background-color: var(--background-fill-secondary);
    border: 1px solid var(--border-color-accent);
    color: var(--text-color-primary);
    padding: 2px 10px;
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: var(--font-weight-medium);
}

/* Divider line */
.summary-divider {
    height: 1px;
    background-color: var(--border-color-primary);
}

/* Bottom summary row (the part that shows the thought) */
.summary-bottom-line {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-md) var(--spacing-lg);
    color: var(--text-color-primary);
    font-weight: var(--font-weight-medium);
}

.summary-title {
    font-size: var(--text-md);
}

/* === NEW: Chevron Icon (CSS Triangle) === */
.summary-chevron {
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid var(--text-color-secondary); /* This creates the downward-pointing triangle */
    transition: transform 0.2s ease-in-out;
}
/* Rotate chevron when the details element is open */
.thoughts-details[open] > .thoughts-summary .summary-chevron {
    transform: rotate(180deg);
}

/* === NEW: Expand/Collapse Text Visibility === */
.collapse-text {
    display: none;
}
.thoughts-details[open] > .thoughts-summary .expand-text {
    display: none;
}
.thoughts-details[open] > .thoughts-summary .collapse-text {
    display: inline;
}


/* The actual content panel that holds the thoughts */
.thoughts-panel-container {
    padding: 0 var(--spacing-lg) var(--spacing-lg) var(--spacing-lg);
    border-top: 1px solid var(--border-color-primary);
}

/* Item styling inside the panel */
.thought-item {
    padding: var(--spacing-lg) 0;
    border-bottom: 1px solid var(--border-color-primary);
    color: var(--text-color-primary);
}
.thought-item:last-child { border-bottom: none; padding-bottom: 0; }
.thought-item p { margin-top: 0; margin-bottom: var(--spacing-md); line-height: 1.6; font-size: var(--text-md); }
.thought-item code { background-color: var(--background-fill-primary); border: 1px solid var(--border-color-primary); padding: 2px 6px; border-radius: var(--radius-sm); font-size: var(--font-mono-size); }
.thought-item pre { background-color: var(--background-fill-primary); border: 1px solid var(--border-color-primary); border-radius: var(--radius-md); padding: var(--spacing-lg); overflow-x: auto; }
.thought-item pre code { background-color: transparent; border: none; padding: 0; }

.gradio-container {
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
}

/* 2. Make all intermediate containers pass the flex sizing down. */
.gradio-container > .main, .gradio-container > .main > .wrap {
    flex-grow: 1;
    overflow: hidden; /* Critical: parents must not scroll */
    display: flex;
    flex-direction: column;
}

/* 3. Target the ChatInterface component itself. */
.chatinterface {
    flex-grow: 1;
    overflow: hidden; /* Critical: parents must not scroll */
    display: flex;
    flex-direction: column;
}

/* 4. Target the chatbot panel. It should grow to fill the space but NOT scroll.
      The min-height: 0 is a key flexbox trick to allow shrinking. */
#chatbot {
    flex-grow: 1 !important;
    overflow: hidden !important; /* This element does NOT scroll. */
    min-height: 0 !important;
}

/* 5. Target the actual message list inside the chatbot.
      THIS is the one and only element that should scroll. */
#chatbot > .bubble-wrap {
    overflow-y: auto !important;
}

/* This styles the track (the part the scrollbar handle slides in) */
#chatbot .bubble-wrap::-webkit-scrollbar-track {
  background: transparent; /* Makes the track invisible */
}

/* This styles the draggable scrollbar handle */
#chatbot .bubble-wrap::-webkit-scrollbar-thumb {
  background-color: #555;    /* A medium gray color for the handle */
  border-radius: 10px;       /* Makes the handle have rounded corners */
  border: 2px solid #333;    /* Creates a small border/padding effect */
}

/* This makes the handle lighter when you hover over it */
#chatbot .bubble-wrap::-webkit-scrollbar-thumb:hover {
  background-color: #777;
}

/* --- For Firefox --- */
/* Firefox has a simpler way of styling scrollbars */
#chatbot .bubble-wrap {
  scrollbar-width: thin; /* Can be "auto", "thin", or "none" */
  scrollbar-color: #555 #333; /* Sets the color of the thumb and the track */
}

.adk-source-number {
    font-weight: bold;
    margin-right: 8px;
    color: #a0a0a0; /* A light gray color, adjust as needed */
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