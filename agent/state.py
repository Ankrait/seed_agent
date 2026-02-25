from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages, AnyMessage


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    temp: str
