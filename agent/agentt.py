from datetime import datetime

from langchain.agents import create_agent
from agent.prompts import RESEARCHER_INSTRUCTIONS
from agent.research_tools import get_today_str
from agent.state import DeepAgentState
from llm.deepseek import llm

from agent.create_subagent_tool import create_subagent_tool
from agent.research_tools import think_tool, tavily_search
from agent.file_tools import *
from agent.todo_tools import *
from agent.prompts import *

search_sub_agent = create_subagent_tool(
    {
        'description': "Delegate research to the sub-agent researcher. Only give this researcher one topic at a time.",
        "name": "research-agent",
        "prompt": RESEARCHER_INSTRUCTIONS.format(date=get_today_str()),
        "tools": [tavily_search, think_tool]
    },
    llm,
    state_schema=DeepAgentState
)

built_in_tools = [ls, read_file, write_file,
                  write_todos, read_todos, think_tool]

all_tools = [search_sub_agent] + built_in_tools

# Build prompt
SUBAGENT_INSTRUCTIONS = SUBAGENT_USAGE_INSTRUCTIONS.format(
    max_concurrent_research_units=3,
    max_researcher_iterations=3,
    date=datetime.now().strftime("%a %b %-d, %Y"),
)

INSTRUCTIONS = (
    "# TODO MANAGEMENT\n"
    + TODO_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# FILE SYSTEM USAGE\n"
    + FILE_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# SUB-AGENT DELEGATION\n"
    + SUBAGENT_INSTRUCTIONS
)

agent = create_agent(
    tools=all_tools,
    system_prompt=INSTRUCTIONS,
    state_schema=DeepAgentState,
    model=llm,
)
