import operator
from typing import Annotated, List, Literal, TypedDict
from langgraph.graph.message import add_messages, AnyMessage


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

    wish_history: Annotated[List[str], operator.add]
    current_status: Literal['wish'] | Literal['bad']
