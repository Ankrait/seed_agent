

from typing import Annotated, NotRequired
from typing_extensions import TypedDict

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState  # updated 1.0
from langchain.agents import create_agent  # updated 1.0

from langgraph.types import Command

from agent.prompts import TASK_DESCRIPTION_PREFIX
from agent.state import DeepAgentState


class SubAgent(TypedDict):
    name: str
    description: str
    prompt: str
    tools: list[BaseTool]


def create_subagent_tool(subagent: SubAgent, model, state_schema):
    """Create a task delegation tool that enables context isolation through sub-agents.

    This function implements the core pattern for spawning specialized sub-agents with
    isolated contexts, preventing context clash and confusion in complex multi-step tasks.

    Args:
        tools: List of available tools that can be assigned to sub-agents
        subagents: List of specialized sub-agent configurations
        model: The language model to use for all agents
        state_schema: The state schema (typically DeepAgentState)

    Returns:
        A 'task' tool that can delegate work to specialized sub-agents
    """
    _agent = create_agent(
        model, system_prompt=subagent['prompt'], tools=subagent["tools"], state_schema=state_schema
    )

    @tool(description=TASK_DESCRIPTION_PREFIX.format(description=subagent['description']))
    def task(
        description: str,
        state: Annotated[DeepAgentState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        """Delegate a task to a specialized sub-agent with isolated context.

        This creates a fresh context for the sub-agent containing only the task description,
        preventing context pollution from the parent agent's conversation history.
        """
        state["messages"] = [{"role": "user", "content": description}]

        # Execute the sub-agent in isolation
        result = _agent.invoke(state)

        return Command(
            update={
                "messages": [
                    ToolMessage(
                        result["messages"][-1].content, tool_call_id=tool_call_id
                    )
                ],
            }
        )

    return task
