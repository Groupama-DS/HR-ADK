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