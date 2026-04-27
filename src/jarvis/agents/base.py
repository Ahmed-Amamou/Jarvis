from abc import ABC, abstractmethod

from langchain_core.tools import BaseTool


class BaseAgent(ABC):
    @property
    @abstractmethod
    def agent_id(self) -> str:
        ...

    @abstractmethod
    def get_tools(self) -> list[BaseTool]:
        ...

    @abstractmethod
    def get_system_prompt(self) -> str:
        ...
