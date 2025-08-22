import gradio as gr
import os
from agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Bypass the system proxy for localhost communication.
os.environ['NO_PROXY'] = '127.0.0.1,localhost'

# Set up session service and runner
session_service = InMemorySessionService()
runner = Runner(
    app_name="GroupamaAgent",
    agent=root_agent,
    session_service=session_service,
)

async def chat_with_agent(user_input, chat_history, session_id):
    """
    Core asynchronous function to interact with the agent, showing intermediate
    tool calls and appending grounding source citations.
    """
    user_id = "demo_user"
    
    chat_history.append({"role": "user", "content": user_input})

    if not session_id:
        session = await session_service.create_session(app_name="GroupamaAgent", user_id=user_id)
        session_id = session.id
        
    content = types.Content(role="user", parts=[types.Part(text=user_input)])
    
    final_response_text = ""
    citations = []
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            # Optional: Show source count
            if event.grounding_metadata:
                print(f"\nBased on {len(event.grounding_metadata.grounding_chunks)} documents")
        print(event)
        # Now, process the content parts for display
        if not (event.content and event.content.parts):
            continue

        for part in event.content.parts:
            if part.thought:
                thought_text = f"🤔 **Thinking...**\n```plaintext\n{part.thought}\n```"
                chat_history.append({"role": "assistant", "content": thought_text})

            if part.function_call:
                func_name = part.function_call.name
                func_args = dict(part.function_call.args)
                tool_call_text = f"🛠️ **Calling Tool: `{func_name}`**\n```json\n{func_args}\n```"
                chat_history.append({"role": "assistant", "content": tool_call_text})
            
            if part.function_response:
                func_name = part.function_response.name
                func_response = dict(part.function_response.response)
                tool_response_text = f"✅ **Tool Response from `{func_name}`**\n```json\n{func_response}\n```"
                chat_history.append({"role": "assistant", "content": tool_response_text})

            if hasattr(part, 'text') and part.text:
                final_response_text += part.text

    if final_response_text and citations:
        citation_markdown = "\n\n**Sources:**\n"
        for i, source in enumerate(citations):
            citation_markdown += f"{i+1}. [{source['title']}]({source['uri']})\n"
        final_response_text += citation_markdown

    if final_response_text:
        chat_history.append({"role": "assistant", "content": final_response_text})
    
    return chat_history, session_id

async def respond(user_input, chat_history, session_id):
    """
    Gradio response function. Clears the input box and initiates the agent call.
    """
    new_chat_history, new_session_id = await chat_with_agent(user_input, chat_history, session_id)
    return new_chat_history, new_session_id, ""


# Create the Gradio Interface
with gr.Blocks(css="footer {display: none !important}") as demo:
    gr.Markdown("# Chat with Groupama Agent")
    
    session_id_state = gr.State(value=None)
    
    chatbot = gr.Chatbot(
        label="Conversation",
        height=700,
        bubble_full_width=False,
        type='messages'
    )
    
    msg = gr.Textbox(
        label="Your Message",
        placeholder="Type your message here and press Enter...",
        render=False
    )
    
    with gr.Row():
        msg.render()

    msg.submit(
        fn=respond,
        inputs=[msg, chatbot, session_id_state],
        outputs=[chatbot, session_id_state, msg]
    )

if __name__ == "__main__":
    demo.launch()