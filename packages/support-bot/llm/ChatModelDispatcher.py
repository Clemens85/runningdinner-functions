from typing import List, Optional, Type
from langchain_core.prompt_values import PromptValue
from pydantic import BaseModel

from Configuration import Configuration
from llm.ChatGemini import ChatGemini
from llm.ChatModel import ChatModel
from llm.ChatOpenAI import ChatOpenAI
from llm.ChatResponse import ChatResponse
from logger.Log import Log

class ChatModelDispatcher(ChatModel):

    def __init__(self):
        self.models: List[ChatModel] = []
        config = Configuration.from_runnable_config()

        openai_model, gemini_model = None, None
        if config.gemini_enabled:
            gemini_model = ChatGemini(model=config.gemini_model, temperature=config.gemini_temperature)
        if config.openai_enabled:
            openai_model = ChatOpenAI(model=config.openai_model, temperature=config.openai_temperature)

        if config.model_preference == "gemini" and gemini_model is not None:
            self.models.append(gemini_model)
            if openai_model is not None:
                self.models.append(openai_model)
        else:
            if openai_model is not None:
                self.models.append(openai_model)
            if gemini_model is not None:
                self.models.append(gemini_model)    

        if len(self.models) == 0:
            raise ValueError("No LLM models are enabled in the configuration.")

    def invoke(self, prompt: PromptValue, custom_response_class: Optional[Type[BaseModel]] = None) -> ChatResponse:
        preferred_model = self.models[0]
        try:
            return self._invoke_model(preferred_model, prompt, custom_response_class)
        except Exception as e:
            if len(self.models) > 1:
                fallback_model = self.models[1]
                Log.warning("Preferred model %s failed, trying fallback %s", str(preferred_model), str(fallback_model))
                return self._invoke_model(fallback_model, prompt, custom_response_class)
            raise

    def _invoke_model(self, model: ChatModel, prompt: PromptValue, custom_response_class: Optional[Type[BaseModel]]) -> ChatResponse:
        Log.info("Invoking model: %s", str(model))
        try:
            response = model.invoke(prompt, custom_response_class)
            Log.info("Model %s responded successfully", str(model))
            return response
        except Exception as e:
            Log.exception("Model %s failed: %s", str(model), str(e))
            raise

