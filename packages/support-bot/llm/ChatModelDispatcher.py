from typing import List
from langchain_core.prompt_values import ChatPromptValue

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

    def invoke(self, prompt: ChatPromptValue) -> ChatResponse:
        preferred_model = self.models[0]
        try:
            Log.info("Invoking preferred model: %s", str(preferred_model))
            return preferred_model.invoke(prompt)
        except Exception as e:
            if len(self.models) > 1:
                Log.exception("Preferred model %s failed with error: %s", str(preferred_model), str(e))
                fallback_model = self.models[1]
                Log.info("Falling back to model: %s", str(fallback_model))
                return fallback_model.invoke(prompt)
            else:
                raise e

