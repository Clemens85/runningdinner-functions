from typing import Optional, Type

from langchain_core.prompt_values import PromptValue
from pydantic import BaseModel

from llm.ChatModel import ChatModel
from llm.ChatResponse import ChatResponse

class ChatGemini(ChatModel):
    def __init__(self, model: str, temperature: float):
      self.model = model
      self.temperature = temperature

    def invoke(self, prompt: PromptValue, custom_response_class: Optional[Type[BaseModel]] = None) -> ChatResponse:
       return ChatResponse(content=f"Gemini fallback response with model {self.model} at temperature {self.temperature}")

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "ChatGemini"