import gradio as gr
import json
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv
load_dotenv()
# --- Configuration ---
# Replace with your project details
PROJECT_ID = "prj-hackathon-team2"
LOCATION = "europe-west4"
REASONING_ENGINE_ID = "5007228729450037248"

# --- Backend Function to Call the Agent (Corrected) ---
def query_agent(user_input: str) -> dict:
    """
    Sends a query to the Vertex AI Reasoning Engine and returns the full response as a dictionary.
    """
    if not user_input or not user_input.strip():
        # Return a dictionary for the error case
        return {"error": "Please enter a question."}

    try:
        # Initialize the Reasoning Engine client
        reasoning_engine = reasoning_engines.ReasoningEngine(REASONING_ENGINE_ID)

        # The .query() method takes keyword arguments that match the inputs
        # of your agent's main function. The most common is `input`.
        response = reasoning_engine.query(
            input=user_input
        )

        # The response from the SDK is already a dictionary-like object.
        # We can return it directly. The gr.JSON component will handle it.
        return response

    except Exception as e:
        # Return a dictionary for the exception case
        error_message = f"An error occurred: {str(e)}"
        print(error_message) # Also print to console for easier debugging
        return {"error": error_message}

# --- Build the Gradio Web Interface ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Query Your Groupama Agent")
    gr.Markdown(
        "Enter your question in the box below to get a response from the deployed Reasoning Engine."
    )

    with gr.Row():
        text_input = gr.Textbox(
            label="Your Question",
            placeholder="e.g., What are the training opportunities?",
            scale=4
        )
        submit_button = gr.Button("Submit Query", variant="primary", scale=1)

    gr.Markdown("## Full JSON Response")
    json_output = gr.JSON(label="Agent Response")

    # Connect the button click to the backend function
    submit_button.click(
        fn=query_agent,
        inputs=text_input,
        outputs=json_output
    )

# --- Launch the Web App ---
if __name__ == "__main__":
    # This will create a local web server and provide a URL.
    demo.launch()