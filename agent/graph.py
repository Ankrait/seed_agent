from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from agent.node import add_wish, final_stage, get_first_wish
from agent.state import State
from agent.tools import tools


def should_continue(state: State):
    if len(state['wish_history']) < 5:
        return 'add_wish'
    else:
        return 'final_stage'


def build_graph():
    graph = StateGraph(State)

    graph.add_node('get_first_wish', get_first_wish)
    graph.add_node('add_wish', add_wish)
    graph.add_node('final_stage', final_stage)

    graph.add_edge(START, 'get_first_wish')
    graph.add_edge('get_first_wish', 'add_wish')
    graph.add_conditional_edges(
        'add_wish', should_continue, ['add_wish', 'final_stage']
    )
    graph.add_edge('final_stage', END)

    return graph
