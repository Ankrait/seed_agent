from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from agent.node import create_plan_node, take_task_node, tasks_list_node
from agent.state import State, Stage
from agent.tools import read_project_tools


def should_tool_call(state: State):
    if state['messages'][-1].tool_calls:
        return Stage.READ_PROJECT_TOOL

    return Stage.END


def has_tasks_to_do(state: State):
    if state['current_task']:
        return Stage.CREATE_PLAN

    return Stage.END


def build_graph():
    graph = StateGraph(State)

    graph.add_node(Stage.TASKS_LIST, tasks_list_node)
    graph.add_node(Stage.TAKE_TASK, take_task_node)
    graph.add_node(Stage.CREATE_PLAN, create_plan_node)
    graph.add_node(Stage.READ_PROJECT_TOOL, ToolNode(read_project_tools))

    graph.add_edge(Stage.START, Stage.TASKS_LIST)
    graph.add_edge(Stage.TASKS_LIST, Stage.TAKE_TASK)

    graph.add_conditional_edges(
        Stage.TAKE_TASK, has_tasks_to_do,
        [
            Stage.CREATE_PLAN, Stage.END
        ]
    )

    graph.add_conditional_edges(
        Stage.CREATE_PLAN, should_tool_call,
        [Stage.READ_PROJECT_TOOL, Stage.END]
    )
    graph.add_edge(Stage.READ_PROJECT_TOOL, Stage.CREATE_PLAN)

    return graph
