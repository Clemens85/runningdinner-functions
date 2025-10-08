from langchain_core.prompt_values import ChatPromptValue
from openai import OpenAI
from pydantic import BaseModel
from langsmith.wrappers import wrap_openai
from Util import to_openai_messages

class ChatResponse(BaseModel):
    content: str

class ChatOpenAI:
    def __init__(self, model: str, temperature: float):
        self.openai_client = wrap_openai(OpenAI())
        self.model = model
        self.temperature = temperature


    def invoke(self, prompt: ChatPromptValue) -> ChatResponse:
        messages = to_openai_messages(prompt)
        response = self.openai_client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
        )
        answer = response.choices[0].message.content
        return ChatResponse(content=answer)
