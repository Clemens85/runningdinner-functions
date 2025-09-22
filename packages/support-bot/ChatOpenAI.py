from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompt_values import ChatPromptValue
from openai import OpenAI
from pydantic import BaseModel

class ChatResponse(BaseModel):
    content: str


class ChatOpenAI:
    def __init__(self, model: str, temperature: float):
        self.openai_client = OpenAI()
        self.model = model
        self.temperature = temperature


    def invoke(self, prompt: ChatPromptValue) -> ChatResponse:
        messages = self.to_openai_messages(prompt)
        response = self.openai_client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
        )
        answer = response.choices[0].message.content
        return ChatResponse(content=answer)

    def to_openai_messages(self, chat_value) -> list:
        result = []
        for msg in chat_value.messages:
            if isinstance(msg, SystemMessage):
                role = "system"
            elif isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            else:
                raise ValueError(f"Unsupported message type: {type(msg)}")
            result.append({"role": role, "content": msg.content})
        return result