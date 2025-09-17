import datetime

from google.cloud import storage
import gradio as gr
from gradio import Chatbot
from gradio.components.chatbot import MessageDict
import re
import datetime
import os

import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv
load_dotenv()

def generate_download_signed_url_v4(bucket_name, blob_name):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file in a development environment.
    In a production environment, it uses Application Default Credentials.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    env = os.environ.get("ENV")

    try:
        if env == "dev":
            # In a development environment, use the service account key file.
            url = blob.generate_signed_url(
                version="v4",
                # This URL is valid for 15 minutes
                expiration=datetime.timedelta(minutes=15),
                # Allow GET requests using this URL.
                method="GET",
            )
        else:
            # In a production environment, get application default credentials.
            credentials, project_id = google.auth.default()
            auth_request = google.auth.transport.requests.Request()
            credentials.refresh(auth_request)
            service_account_email = credentials.service_account_email

            # Generate the signed URL using the IAM API for signing.
            # This requires the service account to have the "Service Account Token Creator" role.
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=15),
                method="GET",
                service_account_email=service_account_email,
                access_token=credentials.token,
            )
        return url
    except Exception as e:
        # It's a good practice to log the error.
        print(f"Error generating signed URL: {e}")
        # Check if the error is due to missing permissions and provide a helpful message.
        if 'iam.serviceAccounts.signBlob' in str(e):
            error_message = ("The service account is missing the 'Service Account Token Creator' role. "
                             "Please grant this role to the service account.")
            print(error_message)
            # Depending on your application's needs, you might want to raise the exception
            # or return an error response.
            raise  # Or return an error indicator
        raise


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
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    z-index: 1000;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

/*
  2. THIS IS THE MOST IMPORTANT PART.
  We target the intermediate '.styler' div that Gradio inserts inside our Group.
  This element is the direct child of the flex container, so this is where we
  must set the desired size of the modal box itself.
*/
#dislike_overlay > .styler {
    width: 90%;                  /* Use a responsive percentage */
    max-width: 400px; !important; /* Set your desired max-width here */
    box-sizing: border-box;
}

/*
  3. Now, we just tell the '.column' inside to fill the space
  we just created in the '.styler' parent.
*/
#dislike_overlay .column {
    width: 100% !important; /* Fill the parent container */
    background-color: var(--block-background-fill);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-color-primary);
    box-shadow: var(--shadow-drop-lg);
    position: relative;
}

/* Style for the new close button */
#close_dislike_modal_btn {
    position: absolute !important;
    top: 8px !important;
    right: 8px !important;
    background: transparent !important;
    border: none !important;
    font-size: 0.8rem !important; /* Reduced font size */
    font-weight: bold; /* Makes the 'X' a bit thicker */
    color: var(--body-text-color-subdued) !important;
    padding: 0 !important;
    line-height: 1 !important; /* Important for vertical alignment */
    width: 20px !important;
    height: 20px !important;
    min-width: 20px !important;
    cursor: pointer;
    z-index: 10; /* Ensures it's on top of other modal content */
    
    /* Use flexbox to perfectly center the 'X' */
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

#close_dislike_modal_btn:hover {
    color: var(--body-text-color) !important;
    background: var(--background-fill-secondary) !important;
    border-radius: 50% !important;
}
"""