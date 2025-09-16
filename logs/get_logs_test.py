import csv
from google.cloud import logging
from datetime import datetime, timedelta, timezone

def get_cloud_run_logs(project_id, service_name, start_time, end_time, filter_feedback, filter_conversation, output_csv_file):
    """
    Fetches logs from a Google Cloud Run service and saves them to a CSV file.

    Args:
        project_id (str): The Google Cloud project ID.
        service_name (str): The name of the Cloud Run service.
        start_time (datetime): The start of the time range to fetch logs for (UTC).
        end_time (datetime): The end of the time range to fetch logs for (UTC).
        filter_feedback (bool): If True, include logs with "Feedback log:".
        filter_conversation (bool): If True, include logs with "Conversation log:".
        output_csv_file (str): The path to the output CSV file.
    """
    client = logging.Client(project=project_id)

    # Format timestamps for the filter in RFC3339 UTC "Zulu" format.
    start_time_str = start_time.isoformat()
    end_time_str = end_time.isoformat()

    # Base filter for Cloud Run service and time range
    filter_parts = [
        f'resource.type="cloud_run_revision"',
        f'resource.labels.service_name="{service_name}"',
        f'timestamp >= "{start_time_str}"',
        f'timestamp <= "{end_time_str}"',
    ]

    # Add text search filters based on boolean flags
    # This searches within the payload for the specified strings.
    log_type_filters = []
    if filter_feedback:
        log_type_filters.append('"Feedback log:"')
    if filter_conversation:
        log_type_filters.append('"Conversation log:"')

    if log_type_filters:
        filter_parts.append(f"({' OR '.join(log_type_filters)})")

    filter_string = " AND ".join(filter_parts)

    print(f"Using filter: {filter_string}")

    # Get the logger entries
    entries = client.list_entries(filter_=filter_string, order_by=logging.DESCENDING)

    # Process and write to CSV
    with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'timestamp',
            'log_type',
            'message_id',
            'user_id',
            'session_id',
            'question',
            'answer',
            'liked',
            'dislike_reason',
            'insertId',
            'logName'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for entry in entries:
            # CORRECTED: Use entry.payload and check if it is a dictionary
            payload = entry.payload
            
            # We only process entries where the payload is a dictionary (JSON payload)
            if isinstance(payload, dict):
                writer.writerow({
                    'timestamp': entry.timestamp,
                    'log_type': payload.get('log_type'),
                    'message_id': payload.get('message_id'),
                    'user_id': payload.get('user_id'),
                    'session_id': payload.get('session_id'),
                    'question': payload.get('question', {}).get('content') if isinstance(payload.get('question'), dict) else payload.get('question'),
                    'answer': payload.get('answer', {}).get('content') if isinstance(payload.get('answer'), dict) else payload.get('answer'),
                    'liked': payload.get('liked'),
                    'dislike_reason': payload.get('dislike_reason'),
                    'insertId': entry.insert_id,
                    'logName': entry.log_name,
                })

    print(f"Logs have been written to {output_csv_file}")

if __name__ == '__main__':
    # --- Configuration ---
    PROJECT_ID = "prj-test-hrminds"  # Your Google Cloud project ID
    SERVICE_NAME = "hr-chatbot-service"  # Your Cloud Run service name
    OUTPUT_CSV_FILE = "logs/logs_test.csv"

    # --- Time Filter ---
    # Fetch logs for the last 24 hours.
    # The timezone is set to UTC to align with Google Cloud Logging standards.
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=1)

    # --- Log Type Filters ---
    FILTER_FEEDBACK_LOGS = True
    FILTER_CONVERSATION_LOGS = True  # Set to True to also include conversation logs

    get_cloud_run_logs(
        project_id=PROJECT_ID,
        service_name=SERVICE_NAME,
        start_time=start_time,
        end_time=end_time,
        filter_feedback=FILTER_FEEDBACK_LOGS,
        filter_conversation=FILTER_CONVERSATION_LOGS,
        output_csv_file=OUTPUT_CSV_FILE
    )