from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from logger.Log import Log
from PromptsV2 import REFINE_QUERY_SYSTEM_PROMPT, REFINE_QUERY_USER_PROMPT, TRANSLATION_PROMPT
from llm.ChatModelDispatcher import ChatModelDispatcher

class RefinedQuery(BaseModel):
    refined_query: str
    detected_language: str

class QueryRefiner:
  def __init__(self, llm_dispatcher: ChatModelDispatcher):
     self.llm_dispatcher = llm_dispatcher

  def refine_query(self, query: str) -> RefinedQuery:

    user_prompt = REFINE_QUERY_USER_PROMPT.invoke({
      "query": query
    })
    prompt_template = ChatPromptTemplate([
      SystemMessage(content=REFINE_QUERY_SYSTEM_PROMPT),
      HumanMessage(content=user_prompt.to_string())
    ])

    final_prompt_value = prompt_template.invoke({})
    response = self.llm_dispatcher.invoke(final_prompt_value, custom_response_class=RefinedQuery)
    return self._extract_refined_query_safe(response.content)

  def _extract_refined_query_safe(self, response_content: str) -> RefinedQuery:
      try:
          return RefinedQuery.model_validate_json(response_content)
      except Exception as e:
          Log.error("Failed to parse refined query response: %s", str(e))
          return RefinedQuery(refined_query=response_content, detected_language="de")
      
  def translate_message_if_needed(self, text: str, original_user_language: str) -> str:
      # Response of LLM will always be in German already if original language is German:
      if original_user_language.lower() == "de":
          return text
      
      # Otherwise, it might happen that the LLM still responds in German even though the original language is not German.
      # This is due to the example support converesations being in German only which very likely influences the LLM to respond in German as well.
      Log.info(f"Translating incoming text from German to '{original_user_language}' if necessary...")

      user_prompt = TRANSLATION_PROMPT.invoke({
          "text": text,
          "language_code": original_user_language
      })
      prompt_template = ChatPromptTemplate([
          SystemMessage(content="You are a helpful assistant that is an expert in detecting languages and in performing translations from German text to another language."),
          HumanMessage(content=user_prompt.to_string())
      ])
      final_prompt_value = prompt_template.invoke({})
      response = self.llm_dispatcher.invoke(final_prompt_value)
      return response.content