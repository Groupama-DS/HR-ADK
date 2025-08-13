from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
import os
from.sub_agents.ami.ami_agent import ami_agent
from.sub_agents.training.training_agent import training_agent
from.sub_agents.salarizare_vanzari.salarizare_vanzari_agent import salarizare_vanzari_agent
from.sub_agents.relatii_munca.relatii_munca_agent import relatii_munca_agent
from.sub_agents.logistica.logistica_agent import logistica_agent
from.sub_agents.beneficii.beneficii_agent import beneficii_agent
from.sub_agents.evaluarea_performantei.evaluarea_performantei_agent import evaluarea_performantei_agent
from dotenv import load_dotenv
from agent.constants import MODEL
from.callbacks.state_callback import init_state
load_dotenv()

# Read the prompt ^_^
with open(os.path.join(os.path.dirname(__file__), 'menu_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

root_agent = LlmAgent(
    name="menu_agent",
    model=MODEL,
    description=(
        "This agent acts as the main orchestrator for answering user questions about internal benefits "
        "and information related to Groupama Insurance Company. It intelligently routes queries to specialized sub-agents,"
        " such as those handling AMI, bonus, training, salarizare vanzari, relatii munca, logistica, beneficii, and evaluarea performantei topics, ensuring accurate and comprehensive responses about company policies,"
        " employee benefits, and other internal resources."
    ),
    instruction=prompt,
    output_key="menu_output",
    tools=[
        AgentTool(agent=ami_agent),
        AgentTool(agent=training_agent),
        AgentTool(agent=salarizare_vanzari_agent),
        AgentTool(agent=relatii_munca_agent),
        AgentTool(agent=logistica_agent),
        AgentTool(agent=beneficii_agent),
        AgentTool(agent=evaluarea_performantei_agent)
    ],
    before_agent_callback=init_state
)
