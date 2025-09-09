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
/* The wrapper is no longer needed, but styling the components is. */
.sources-details, .thoughts-details {
    border: 1px solid var(--border-color-primary);
    border-radius: var(--radius-lg);
    padding: var(--spacing-sm);
    margin-top: var(--spacing-md);
    background-color: var(--background-fill-secondary);
}
.thoughts-streaming {
    border: 1px solid var(--border-color-primary);
    border-radius: var(--radius-lg);
    padding: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
    background-color: var(--background-fill-secondary);
}
/* ... all other styling for cards, summaries, etc. remains the same ... */
.sources-details summary, .thoughts-details summary {
    cursor: pointer; font-weight: bold; font-size: 0.9em; color: var(--body-text-color);
    padding: var(--spacing-xs); outline: none; list-style: none;
}
.sources-details summary::-webkit-details-marker, .thoughts-details summary::-webkit-details-marker { display: none; }
.sources-details summary::before, .thoughts-details summary::before { content: '▶ '; font-size: 0.8em; }
.sources-details[open] summary::before, .thoughts-details[open] summary::before { content: '▼ '; }
.sources-container {
    display: flex; overflow-x: auto; gap: var(--spacing-lg); margin-top: var(--spacing-sm);
    padding-top: var(--spacing-sm); border-top: 1px solid var(--border-color-primary);
}
.source-card {
    flex: 0 0 280px; width: 280px; border: 1px solid var(--border-color-primary);
    border-radius: var(--radius-lg); padding: var(--spacing-md); background-color: var(--block-background-fill);
    box-shadow: var(--shadow-drop); display: flex; flex-direction: column;
}
.source-content {
    height: 140px; overflow-y: auto; border: 1px solid var(--border-color-primary);
    padding: var(--spacing-sm); border-radius: var(--radius-md); font-size: 0.85em;
    line-height: 1.4; margin-bottom: var(--spacing-sm); color: var(--body-text-color-subdued);
}
.source-title {
    text-align: center; text-decoration: none; color: var(--link-text-color); font-weight: bold;
    font-size: 0.9em; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.source-title:hover { text-decoration: underline; color: var(--link-text-color-hover); }
.summary-closed, .summary-open { font-weight: normal; color: var(--body-text-color-subdued); }
.thoughts-details .summary-open { display: none; }
.thoughts-details[open] .summary-closed { display: none; }
.thoughts-details[open] .summary-open { display: inline; }
.thoughts-panel-container { margin-top: var(--spacing-sm); padding-top: var(--spacing-sm); border-top: 1px solid var(--border-color-primary); }
.collapse-text { text-align: left; font-size: 0.9em; color: var(--body-text-color-subdued); margin-top: var(--spacing-sm); cursor: pointer; }


#dislike_overlay {
    position: fixed; /* Takes the element out of the normal document flow */
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6); /* Semi-transparent backdrop */
    z-index: 1000; /* Ensures it's on top of all other elements */
    display: flex; /* Uses flexbox to center the content */
    justify-content: center;
    align-items: center;
    padding: 20px;
}

/* Style the inner column holding the textbox and button */
#dislike_overlay > .gr-column {
    background-color: var(--block-background-fill);
    padding: var(--spacing-xxl);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-color-primary);
    box-shadow: var(--shadow-drop-lg);
    width: 90%;
    max-width: 550px; /* Prevents it from being too wide on large screens */
}

"""