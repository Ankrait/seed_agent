from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from agent.node import call_model
from agent.state import State
from agent.tools import get_weather


def should_tool_call(state: State):
    if state['messages'][-1].tool_calls:
        return 'tool_call'
    else:
        return END


def build_graph():
    graph = StateGraph(State)

    graph.add_node('call_model', call_model)
    graph.add_node('tool_call', ToolNode([get_weather]))

    graph.add_edge(START, 'call_model')
    graph.add_edge('tool_call', 'call_model')
    graph.add_conditional_edges(
        'call_model', should_tool_call, ['tool_call', END]
    )

    return graph
