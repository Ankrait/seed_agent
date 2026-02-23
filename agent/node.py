from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from agent.prompts import BAD_PROMPT, WISH_PROMPT
from agent.state import State
from agent.tools import tools
from llm.deepseek import llm

llm_with_tools = llm.bind_tools(tools)


def get_first_wish(state: State):
    return {'wish_history': [state.get('messages')[-1].content], 'current_status': 'bad'}


def add_wish(state: State):
    current_status = state.get('current_status')
    if current_status == 'wish':
        prompt = WISH_PROMPT
        new_status = 'bad'
    else:
        prompt = BAD_PROMPT
        new_status = 'wish'

    response = llm_with_tools.invoke([
        SystemMessage(prompt),
        HumanMessage(f'Текущее желание: {state.get('wish_history')[-1]}')
    ])

    return {'wish_history': [response.content], 'current_status': new_status}


def final_stage(state: State):
    return {'messages': [AIMessage(state.get('wish_history')[-1])]}
