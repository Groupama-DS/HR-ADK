from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.planners import BuiltInPlanner
from google.genai import types

import os
# from.sub_agents.ami.ami_agent import ami_agent
# from.sub_agents.training.training_agent import training_agent
# from.sub_agents.salarizare_vanzari.salarizare_vanzari_agent import salarizare_vanzari_agent
# from.sub_agents.relatii_munca.relatii_munca_agent import relatii_munca_agent
# from.sub_agents.logistica.logistica_agent import logistica_agent
# from.sub_agents.beneficii.beneficii_agent import beneficii_agent
# from.sub_agents.evaluarea_performantei.evaluarea_performantei_agent import evaluarea_performantei_agent
from dotenv import load_dotenv
from agent.constants import MODEL

from .tools.ami_rag_tool import ami_datastore_tool
from .tools.beneficii_rag_tool import beneficii_datastore_tool
from .tools.evaluarea_performantei_rag_tool import evaluarea_performantei_datastore_tool
from .tools.logistica_rag_tool import logistica_datastore_tool
from .tools.relatii_munca_rag_tool import relatii_munca_datastore_tool
from .tools.salarizare_vanzari_rag_tool import salarizare_vanzari_datastore_tool
from .tools.training_rag_tool import training_datastore_tool
from .callbacks.grounding_callback import save_grounding_metadata_to_state
from .callbacks.before_tool_callback import simple_after_tool_modifier

load_dotenv()

#TODO Example Store

# Read the prompt ^_^
with open(os.path.join(os.path.dirname(__file__), 'menu_prompt.md'), encoding='utf-8') as f:
    prompt = f.read()

# 1. Create a ThinkingConfig to ask the model for its thoughts.
thinking_config = types.ThinkingConfig(
    include_thoughts=True,  # Key parameter to enable thinking output
)

# 2. Instantiate the BuiltInPlanner with the config.
planner = BuiltInPlanner(thinking_config=thinking_config)

root_agent = LlmAgent(
    name="menu_agent",
    model=MODEL,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            )
        ]
    ),
    description=(
        "Un asistent virtual pentru angajați, capabil să răspundă la întrebări specifice prin căutarea"
        " în documentația internă a companiei. Utilizează unelte de căutare dedicate pentru a oferi informații despre "
        "AMI(Asigurarea Medicala Integrala), training, salarizare vanzari, relatii munca, logistica, beneficii si evaluarea performantei"
    ),
    instruction=prompt,
    output_key="menu_output",
    planner=planner,
    tools=[
        ami_datastore_tool,
        beneficii_datastore_tool,
        evaluarea_performantei_datastore_tool,
        logistica_datastore_tool,
        relatii_munca_datastore_tool,
        salarizare_vanzari_datastore_tool,
        training_datastore_tool,
    ],
    after_tool_callback=simple_after_tool_modifier,
)
