from abc import ABC, abstractmethod

from langchain_core.prompt_values import ChatPromptValue

from llm.ChatResponse import ChatResponse

class ChatModel(ABC):
    @abstractmethod
    def invoke(self, prompt: ChatPromptValue) -> ChatResponse:
        pass