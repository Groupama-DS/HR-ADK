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

from .tools.ami_rag_tool import ami_datastore_tool
from .tools.beneficii_rag_tool import beneficii_datastore_tool
from .tools.evaluarea_performantei_rag_tool import evaluarea_performantei_datastore_tool
from .tools.logistica_rag_tool import logistica_datastore_tool
from .tools.relatii_munca_rag_tool import relatii_munca_datastore_tool
from .tools.salarizare_vanzari_rag_tool import salarizare_vanzari_datastore_tool
from .tools.training_rag_tool import training_datastore_tool
from .callbacks.grounding_callback import save_grounding_metadata_to_state

load_dotenv()

#TODO Example Store

# Read the prompt ^_^
with open(os.path.join(os.path.dirname(__file__), 'menu_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

root_agent = LlmAgent(
    name="menu_agent",
    model=MODEL,
    description=(
        "This agent acts as the main orchestrator for answering user questions about internal benefits "
        "and information related to Groupama Insurance Company. It intelligently routes queries to specialized tools,"
        " such as those handling AMI, bonus, training, salarizare vanzari, relatii munca, logistica, beneficii, and evaluarea performantei topics, ensuring accurate and comprehensive responses about company policies,"
        " employee benefits, and other internal resources."
    ),
    instruction=prompt,
    output_key="menu_output",
    tools=[
        ami_datastore_tool,
        beneficii_datastore_tool,
        evaluarea_performantei_datastore_tool,
        logistica_datastore_tool,
        relatii_munca_datastore_tool,
        salarizare_vanzari_datastore_tool,
        training_datastore_tool,
    ]
)
