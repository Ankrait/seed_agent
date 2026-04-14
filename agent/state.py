from typing import Annotated, Literal, NotRequired, TypedDict
from langchain.agents import AgentState
from langgraph.graph.message import add_messages, AnyMessage


class Todo(TypedDict):
    content: str
    status: Literal["pending", "in_progress", "completed"]


class DeepAgentState(AgentState):
    """Extended agent state that includes task tracking and virtual file system.

    Inherits from LangGraph's AgentState and adds:
    - todos: List of Todo items for task planning and progress tracking
    - files: Virtual file system stored as dict mapping filenames to content
    """

    todos: NotRequired[list[Todo]]


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    temp: str
