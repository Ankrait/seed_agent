from langgraph.graph import StateGraph, START, END
from enum import StrEnum
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages, AnyMessage

from services.tasks import Task


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    tasks: list[Task]

    current_task: Task | None
    plan: str | None


class Stage(StrEnum):
    START = START
    END = END
    READ_PROJECT_TOOL = 'read_project_tool'
    TASKS_LIST = 'tasks_list'
    TAKE_TASK = 'take_task'
    CREATE_PLAN = 'create_plan'
