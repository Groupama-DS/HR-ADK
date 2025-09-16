import csv
from google.cloud import logging
from datetime import datetime, timedelta, timezone
import html
import markdown

def generate_html_report(logs):
    """Generates an HTML report from a list of log dictionaries."""
    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "<title>Logs Report</title>",
        "<style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f9; margin: 0; padding: 1.25rem; }",
        "h1 { text-align: center; color: #444; }",
        ".container { max-width: 100%; box-sizing: border-box; background: white; padding: 1.25rem; box-shadow: 0 0 0.6rem rgba(0,0,0,0.1); border-radius: 0.5rem; }",
        "table { border-collapse: collapse; width: 100%; margin-top: 1.25rem; }",
        "th, td { border: 1px solid #ddd; padding: 0.75rem 1rem; text-align: left; vertical-align: top; }",
        "th { background-color: #f8f8f8; font-weight: bold; }",
        "tr:nth-child(even) { background-color: #fdfdfd; }",
        "tr:hover { background-color: #f1f1f1; }",
        ".answer-content { width: 45vw; word-wrap: break-word; white-space: pre-wrap; }",
        ".answer-content details { border: 1px solid #ccc; border-radius: 0.3rem; padding: 0.6rem; margin-top: 0.6rem; background-color: #f9f9f9; }",
        ".answer-content summary { font-weight: bold; cursor: pointer; outline: none; }",
        "</style>",
        "</head>",
        "<body>",
        "<div class='container'>",
        "<h1>Cloud Run Logs Report</h1>",
        "<table>",
        "<thead><tr>",
        "<th>Timestamp</th>",
        "<th>Log Type</th>",
        "<th>Question</th>",
        "<th>Answer</th>",
        "<th>Liked</th>",
        "<th>Dislike Reason</th>",
        "<th>Message ID</th>",
        "<th>User ID</th>",
        "<th>Session ID</th>",
        "</tr></thead>",
        "<tbody>"
    ]

    for log in logs:
        raw_answer = str(log.get('answer', '') or '')
        # Add markdown="1" to details tags and enable md_in_html extension
        answer_with_attr = raw_answer.replace('<details>', '<details markdown="1">')
        answer_content = markdown.markdown(answer_with_attr, extensions=['md_in_html'])
        question = html.escape(str(log.get('question', '')))
        dislike_reason = html.escape(str(log.get('dislike_reason', ''))) if log.get('dislike_reason') else ''

        timestamp_obj = log.get('timestamp')
        if isinstance(timestamp_obj, datetime):
            # Format to dd/mm/yy and hh:mm:ss on two lines
            formatted_timestamp = timestamp_obj.strftime('%d/%m/%y<br>%H:%M:%S')
        else:
            # Escape if it's not a datetime object we formatted
            formatted_timestamp = html.escape(str(timestamp_obj or ''))

        html_parts.append("<tr>")
        html_parts.append(f"<td>{formatted_timestamp}</td>")
        html_parts.append(f"<td>{html.escape(str(log.get('log_type', '')))}</td>")
        html_parts.append(f"<td>{question}</td>")
        html_parts.append(f"<td class='answer-content'><details><summary>Answer</summary>{answer_content}</details></td>")
        html_parts.append(f"<td>{html.escape(str(log.get('liked', '')))}</td>")
        html_parts.append(f"<td>{dislike_reason}</td>")
        html_parts.append(f"<td>{html.escape(str(log.get('message_id', '')))}</td>")
        html_parts.append(f"<td>{html.escape(str(log.get('user_id', '')))}</td>")
        html_parts.append(f"<td>{html.escape(str(log.get('session_id', '')))}</td>")
        html_parts.append("</tr>")

    html_parts.extend([
        "</tbody>",
        "</table>",
        "</div>",
        "</body>",
        "</html>"
    ])

    return "\n".join(html_parts)


def get_cloud_run_logs(project_id, service_name, start_time, end_time, filter_feedback, filter_conversation, output_csv_file=None, output_html_file=None):
    """
    Fetches logs from a Google Cloud Run service and saves them to a CSV and/or HTML file.

    Args:
        project_id (str): The Google Cloud project ID.
        service_name (str): The name of the Cloud Run service.
        start_time (datetime): The start of the time range to fetch logs for (UTC).
        end_time (datetime): The end of the time range to fetch logs for (UTC).
        filter_feedback (bool): If True, include logs with "Feedback log:".
        filter_conversation (bool): If True, include logs with "Conversation log:".
        output_csv_file (str, optional): The path to the output CSV file.
        output_html_file (str, optional): The path to the output HTML file.
    """
    if not output_csv_file and not output_html_file:
        print("No output file specified. Exiting.")
        return

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

    # Add structured filters for log_type based on boolean flags
    log_type_filters = []
    if filter_feedback:
        log_type_filters.append('jsonPayload.log_type="feedback"')
    if filter_conversation:
        log_type_filters.append('jsonPayload.log_type="conversation"')

    if not log_type_filters:
        print("Both feedback and conversation filters are off. No logs to fetch.")
        return

    filter_parts.append(f"({' OR '.join(log_type_filters)})")

    filter_string = " AND ".join(filter_parts)

    print(f"Using filter: {filter_string}")

    # Get the logger entries
    entries = client.list_entries(filter_=filter_string, order_by=logging.DESCENDING)

    # Collect and process logs
    log_data = []
    for entry in entries:
        payload = entry.payload
        if isinstance(payload, dict):
            log_data.append({
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

    # Write to CSV if path is provided
    if output_csv_file:
        with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'timestamp', 'log_type', 'message_id', 'user_id', 'session_id',
                'question', 'answer', 'liked', 'dislike_reason', 'insertId', 'logName'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(log_data)
        print(f"Logs have been written to {output_csv_file}")

    # Generate and write HTML report if path is provided
    if output_html_file:
        html_report = generate_html_report(log_data)
        with open(output_html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        print(f"HTML report has been written to {output_html_file}")

if __name__ == '__main__':
    # --- Configuration ---
    PROJECT_ID = "prj-test-hrminds"  # Your Google Cloud project ID
    SERVICE_NAME = "hr-chatbot-service"  # Your Cloud Run service name
    OUTPUT_CSV_FILE = "logs/logs_test.csv"
    OUTPUT_HTML_FILE = "logs/logs_report.html"

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
        output_csv_file=OUTPUT_CSV_FILE,
        output_html_file=OUTPUT_HTML_FILE
    )