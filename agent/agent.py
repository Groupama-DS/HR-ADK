from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
import os
from.sub_agents.ami.ami_agent import ami_agent
from.sub_agents.bonus.bonus_agent import bonus_agent
from dotenv import load_dotenv
load_dotenv()

# Read the prompt
with open(os.path.join(os.path.dirname(__file__), 'menu_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

root_agent = LlmAgent(
    name="menu_agent",
    model=os.environ.get("MODEL"),
    description=(
        "This agent acts as the main orchestrator for answering user questions about internal benefits " 
        "and information related to Groupama Insurance Company. It intelligently routes queries to specialized sub-agents,"
        " such as those handling AMI and bonus topics, ensuring accurate and comprehensive responses about company policies,"
        " employee benefits, and other internal resources."
    ),
    instruction=prompt,
    output_key="menu_output",
    tools=[
        AgentTool(agent=ami_agent),
        AgentTool(agent=bonus_agent)
    ]
)
