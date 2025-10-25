from typing import Optional, Type
from langchain_core.prompt_values import PromptValue
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from pydantic import BaseModel
from Util import to_openai_messages
from llm.ChatModel import ChatModel
from llm.ChatResponse import ChatResponse

class ChatOpenAI(ChatModel):
    def __init__(self, model: str, temperature: float):
        self.openai_client = wrap_openai(OpenAI())
        self.model = model
        self.temperature = temperature


    def invoke(self, prompt: PromptValue, custom_response_class: Optional[Type[BaseModel]] = None) -> ChatResponse:

        messages = to_openai_messages(prompt)

        # response_format = NOT_GIVEN
        # if custom_response_class is not None:
        #     response_format = {
        #         "type": "json_schema",
        #         "json_schema": {
        #             "name": custom_response_class.__name__.lower(),
        #             "strict": True,
        #             "schema": custom_response_class.model_json_schema()
        #         }
        #     }

        if custom_response_class is not None:
            response = self.openai_client.responses.parse(
                model=self.model,
                temperature=self.temperature,
                input=messages,
                text_format=custom_response_class,
            )
            answer = response.output_text
            return ChatResponse(content=answer, is_structured=True)
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
        )
        answer = response.choices[0].message.content
        return ChatResponse(content=answer, is_structured=False)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"ChatOpenAI {self.model} with temperature {self.temperature}"