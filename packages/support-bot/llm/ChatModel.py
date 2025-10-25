from abc import ABC, abstractmethod
from typing import Optional, Type

from langchain_core.prompt_values import PromptValue
from pydantic import BaseModel

from llm.ChatResponse import ChatResponse

class ChatModel(ABC):
    @abstractmethod
    def invoke(self, prompt: PromptValue, custom_response_class: Optional[Type[BaseModel]] = None) -> ChatResponse:
        pass