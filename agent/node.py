from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from agent.prompts import CREATE_PLAN_SYSTEM_PROMPT, CREATE_PLAN_USER_PROMPT
from agent.state import State
from agent.tools import read_project_tools
from llm.deepseek import llm
from services.tasks import get_tasks_list


async def tasks_list_node(state: State) -> State:
    tasks = await get_tasks_list()
    return {'tasks': tasks}


async def take_task_node(state: State) -> State:
    return {'current_task': state["tasks"][0], 'tasks': state["tasks"][1:]}


def create_plan_node(state: State) -> State:
    current_task = state.get('current_task')

    messages = state.get('messages', [])

    if len(messages) > 0 and isinstance(messages[-1], ToolMessage):
        print(messages[-1])

    if len(messages) == 0:
        messages = [
            SystemMessage(CREATE_PLAN_SYSTEM_PROMPT),
            HumanMessage(
                CREATE_PLAN_USER_PROMPT.format(
                    current_task=f"Название: {current_task.title}\nОписание: {current_task.description}"
                )
            )
        ]

    result = llm.bind_tools(read_project_tools).invoke(
        messages
    )

    print(result)

    messages.append(result)

    return {'messages': [result]}
