from agent.state import State
from agent.tools import get_weather
from llm.openai import llm


def call_model(state: State):
    result = llm.bind_tools([get_weather]).invoke(state['messages'])
    return {'messages': [result]}
