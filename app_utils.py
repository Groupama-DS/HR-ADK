import datetime

from google.cloud import storage


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