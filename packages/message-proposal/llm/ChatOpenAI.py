from typing import Optional, Type, Iterable
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionDeveloperMessageParam, ChatCompletionSystemMessageParam, ChatCompletionAssistantMessageParam, \
    ChatCompletionFunctionMessageParam, ChatCompletionToolMessageParam
from pydantic import BaseModel

from llm.ChatResponse import ChatResponse


class ChatOpenAI:
    def __init__(self, model: str, temperature: float):
        self.openai_client = wrap_openai(OpenAI())
        self.model = model
        self.temperature = temperature

    def invoke(self,
               prompt: Iterable[ChatCompletionDeveloperMessageParam | ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam | ChatCompletionToolMessageParam | ChatCompletionFunctionMessageParam],
               custom_response_class: Optional[Type[BaseModel]] = None,
               model_override: str = None,
               temperature_override: float = None) -> ChatResponse:

        model_to_use = model_override if model_override is not None else self.model
        temperature_to_use = temperature_override if temperature_override is not None else self.temperature

        if custom_response_class is not None:
            response = self.openai_client.responses.parse(
                model=model_to_use,
                temperature=temperature_to_use,
                input=prompt,
                text_format=custom_response_class,
            )
            answer = response.output_text
            return ChatResponse(content=answer, is_structured=True)

        response = self.openai_client.chat.completions.create(
            model=model_to_use,
            temperature=temperature_to_use,
            messages=prompt,
        )
        answer = response.choices[0].message.content
        return ChatResponse(content=answer, is_structured=False)

    def embed_text(self, text: str, embedding_model = 'text-embedding-3-small') -> list[float]:
        response = self.openai_client.embeddings.create(
            input=text,
            model=embedding_model
        )
        embedding = response.data[0].embedding
        return embedding

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"ChatOpenAI {self.model} with temperature {self.temperature}"