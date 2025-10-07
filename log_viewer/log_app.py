from flask import Flask, render_template, request
from google.cloud import logging
from datetime import datetime, timedelta, timezone
import html
import markdown

app = Flask(__name__)

# --- Configuration ---
PROJECT_IDS = ["prj-prod-hrminds", "prj-test-hrminds", "prj-hackathon-team2"]
SERVICE_NAME = "hr-chatbot-service"  # Your Cloud Run service name

def get_cloud_run_logs(project_id, service_name, start_time, end_time, filter_feedback, filter_conversation):
    """
    Fetches logs from a Google Cloud Run service.

    Args:
        project_id (str): The Google Cloud project ID.
        service_name (str): The name of the Cloud Run service.
        start_time (datetime): The start of the time range to fetch logs for (UTC).
        end_time (datetime): The end of the time range to fetch logs for (UTC).
        filter_feedback (bool): If True, include logs with log_type="feedback".
        filter_conversation (bool): If True, include logs with log_type="conversation".
    
    Returns:
        list: A list of log dictionaries.
    """
    client = logging.Client(project=project_id)

    start_time_str = start_time.isoformat()
    end_time_str = end_time.isoformat()

    filter_parts = [
        f'resource.type="cloud_run_revision"',
        f'resource.labels.service_name="{service_name}"',
        f'timestamp >= "{start_time_str}"',
        f'timestamp <= "{end_time_str}"',
    ]

    log_type_filters = []
    if filter_feedback:
        log_type_filters.append('jsonPayload.log_type="feedback"')
    if filter_conversation:
        log_type_filters.append('jsonPayload.log_type="conversation"')

    if not log_type_filters:
        print("Both feedback and conversation filters are off. No logs to fetch.")
        return []

    filter_parts.append(f"({' OR '.join(log_type_filters)})")
    filter_string = " AND ".join(filter_parts)
    print(f"Using filter: {filter_string}")

    entries = client.list_entries(filter_=filter_string, order_by=logging.DESCENDING)

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
            })
    return log_data

def generate_table_body(logs):
    """Generates HTML table body rows from a list of log dictionaries."""
    html_parts = []
    for log in logs:
        raw_answer = str(log.get('answer', '') or '')
        answer_with_attr = raw_answer.replace('<details>', '<details markdown="1">')
        answer_content = markdown.markdown(answer_with_attr, extensions=['markdown.extensions.md_in_html'])
        question = html.escape(str(log.get('question', '')))
        dislike_reason = html.escape(str(log.get('dislike_reason', ''))) if log.get('dislike_reason') else ''

        timestamp_obj = log.get('timestamp')
        if isinstance(timestamp_obj, datetime):
            formatted_timestamp = timestamp_obj.strftime('%d/%m/%y<br>%H:%M:%S')
        else:
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
    return "\n".join(html_parts)

@app.route('/')
def report():
    is_first_load = not request.args

    project_id = request.args.get('project_id', PROJECT_IDS[0])

    end_time_str = request.args.get('end_time')
    start_time_str = request.args.get('start_time')
    
    feedback = 'feedback' in request.args or is_first_load
    conversation = 'conversation' in request.args or is_first_load

    if end_time_str:
        end_time = datetime.fromisoformat(end_time_str).replace(tzinfo=timezone.utc)
    else:
        end_time = datetime.now(timezone.utc)

    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str).replace(tzinfo=timezone.utc)
    else:
        start_time = end_time - timedelta(days=1)

    logs = get_cloud_run_logs(
        project_id=project_id,
        service_name=SERVICE_NAME,
        start_time=start_time,
        end_time=end_time,
        filter_feedback=feedback,
        filter_conversation=conversation
    )

    table_body = generate_table_body(logs)

    return render_template('report.html',
        table_body=table_body,
        start_time=start_time.strftime('%Y-%m-%dT%H:%M'),
        end_time=end_time.strftime('%Y-%m-%dT%H:%M'),
        feedback=feedback,
        conversation=conversation,
        project_ids=PROJECT_IDS,
        selected_project_id=project_id
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
