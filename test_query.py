import os
import sys
import asyncio
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.run_config import RunConfig
from google.adk.agents.run_config import StreamingMode

# --- KEY CHANGE ---
# Remove all the placeholder agent code and simply import your real agent.
# This assumes your agent.py file is in a subfolder named 'agent'.
from agent.agent import root_agent

# Bypass the system proxy for localhost communication.
os.environ['NO_PROXY'] = '127.0.0.1,localhost'

# Set up session service and runner with your imported agent
session_service = InMemorySessionService()
runner = Runner(
    app_name="GroupamaAgent",
    agent=root_agent,  # Use your imported LlmAgent here
    session_service=session_service,
)
user_id = "demo_user"
session = None
session_id = None


async def chat_with_agent(message, history):
    """
    Initiates a chat with the agent and yields response chunks as they arrive.
    """
    global session, session_id
    if session is None or session_id is None:
        session = await session_service.create_session(app_name="GroupamaAgent", user_id=user_id)
        session_id = session.id

    # This variable keeps track of the length of the text we've already yielded.
    yielded_text_length = 0

    content = types.Content(role="user", parts=[types.Part(text=message)])

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
        run_config=RunConfig(
            streaming_mode=StreamingMode.SSE
        )
    ):
        print(f"########################## NEW PART EVENT #####################\n\n\n\n{event}")
        if event.content and event.content.parts:
            # Re-join all parts received so far to get the current full response
            assistant_response_parts = [
                part.text for part in event.content.parts if hasattr(part, 'text') and part.text
            ]
            full_response_so_far = "".join(assistant_response_parts)

            # Calculate the new portion of text that hasn't been yielded yet
            new_text = full_response_so_far[yielded_text_length:]

            if new_text:
                # Yield only the new chunk of text
                yield new_text
                # Update our tracker to the new total length
                yielded_text_length = len(full_response_so_far)


if __name__ == "__main__":
    async def main():
        """
        Main function to run the chat and print the streaming response.
        """
        user_question = "scrie in 1000 de cuvinte ce subiecte stii"
        print(f"You: {user_question}")
        print("Agent: ", end="", flush=True)

        # Iterate through the chunks of the response from the agent
        async for response_chunk in chat_with_agent(user_question, []):
            # Print each chunk as it arrives without adding a newline
            print(response_chunk, end="", flush=True)

        # Print a final newline to clean up the terminal prompt
        print()

    # Run the asynchronous main function
    asyncio.run(main())