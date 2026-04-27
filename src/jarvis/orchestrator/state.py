from typing import Annotated, TypedDict

from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class JarvisState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str | None
    agent_output: str | None
    memory_context: list[str]
    session_id: str
