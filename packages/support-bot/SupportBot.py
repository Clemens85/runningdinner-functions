from datetime import datetime
from typing import List, Optional, Sequence

from langchain_core.prompt_values import PromptValue
from typing_extensions import Annotated, TypedDict
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from langgraph.graph import START, END, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from PromptsV2 import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, EXAMPLE_CONVERSATION_DOC_TEMPLATE, ADMIN_SOFTWARE_FEATURES, \
    FEATURES_SECTION_TEMPLATE, EXAMPLES_SECTION_TEMPLATE, SELF_SERVICE_SOFTWARE_FEATURES, LANDING_SOFTWARE_FEATURES
from QueryRefiner import QueryRefiner, RefinedQuery
from SupportDocument import SupportDocument
from UserRequest import UserRequest
from VectorDbRepository import VectorDbRepository
from llm.ChatModelDispatcher import ChatModelDispatcher

from memory.MemoryProvider import MemoryProvider
from Configuration import Configuration
from RequestParamsParser import PUBLIC_EVENT_ID_KEY, RequestParamsParser

from api.RunningDinnerApi import RunningDinnerApi
from logger.Log import Log
# from IPython.display import Image, display

class State(TypedDict, total=False):
  messages: Annotated[Sequence[BaseMessage], add_messages]
  docs: List[SupportDocument]
  question: str
  question_refined: str
  question_language: str
  answer: str
  request_params: dict[str, str]
  public_event_id: Optional[str]
  user_context: Optional[str]
  admin_id: Optional[str]
  
class SupportBot:
  
  def __init__(self, memory_provider: MemoryProvider, vector_db_repository: VectorDbRepository, thread_id: str):
    self.llm_model_dispatcher = ChatModelDispatcher()
    self.vector_db = vector_db_repository
    self.memory_provider = memory_provider
    self.query_refiner = QueryRefiner(self.llm_model_dispatcher)
    self.thread_id = thread_id

  def build_workflow_graph(self):
    builder = StateGraph(state_schema=State)
    
    builder.add_node("refine_query", self.refine_query)
    builder.add_node("fetch_event_context", self.fetch_event_context)
    builder.add_node("retrieve_example_conversations", self.retrieve_example_conversations)
    builder.add_node("answer_with_context", self.answer_with_context)
    
    builder.add_edge(START, "refine_query")
    builder.add_edge(START, "fetch_event_context")

    builder.add_edge("refine_query", "retrieve_example_conversations")

    # builder.add_edge("refine_query", "fetch_event_context")

    builder.add_edge(["retrieve_example_conversations", "fetch_event_context"], "answer_with_context")
    builder.add_edge("answer_with_context", END)
    
    return builder.compile(checkpointer=self.memory_provider.get())
  
  def refine_query(self, state: State):
    Log.info(f"Calling refine_query in Thread ID {self.thread_id}")
    question = state["question"]
    query_refined: RefinedQuery = self.query_refiner.refine_query(question)
    Log.info(f"Refined question for language code {query_refined.detected_language} in Thread ID {self.thread_id}")
    return { "question_refined": query_refined.refined_query, "question_language": query_refined.detected_language }

  def fetch_event_context(self, state: State, config: RunnableConfig):
    Log.info(f"Calling fetch_event_context in Thread ID {self.thread_id}")
    request_params = state.get("request_params") or {}
    event_ids = RequestParamsParser.parse(request_params)

    public_event_id = event_ids.get(PUBLIC_EVENT_ID_KEY) or ""
    if len(public_event_id) <= 0:
      Log.info(f"No public event context available in Thread ID {self.thread_id}")
      return {}

    configurable = Configuration.from_runnable_config(config)
    host = configurable.runningdinner_api_host
    try:
      api = RunningDinnerApi(host)
      public_event_info = api.get_public_event_info(public_event_id)
      Log.info(f"Retrieved public event info for {public_event_id} within Thread ID f{self.thread_id}: {public_event_info}")
      return { "user_context": public_event_info }
    except Exception as e:
      Log.error(f"Error fetching public event info for public event id {public_event_id} within Thread ID f{self.thread_id}: {e}")
      return {}

  def retrieve_example_conversations(self, state: State, config: RunnableConfig):
      Log.info(f"Calling retrieve_example_conversations in Thread ID {self.thread_id}")
      question = self._get_question_from_state(state)

      configurable = Configuration.from_runnable_config(config)
      k = configurable.max_similar_docs

      if state.get("docs") is not None and len(state.get("docs")) > 0:
        Log.info(f"Already {len(state['docs'])} documents in state, no need to do further rag retrieval in Thread ID {self.thread_id}")
        return {}

      docs = self.vector_db.retrieve(query = question, top_k = k)
      return { "docs": docs }
  
  def answer_with_context(self, state: State):
    Log.info(f"Calling answer_with_context in Thread ID {self.thread_id}")

    user_question = self._get_question_from_state(state)
    docs = state.get("docs") or []

    Log.info(f"Got {len(docs)} documents as context in Thread ID {self.thread_id}")

    features_section = ""
    if not self._is_followup_question(state):
        all_features = ADMIN_SOFTWARE_FEATURES + "\n\n" + SELF_SERVICE_SOFTWARE_FEATURES + "\n\n" + LANDING_SOFTWARE_FEATURES
        # Features always have the latest state
        features_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        features_section = FEATURES_SECTION_TEMPLATE.invoke({
            "features": all_features,
            "features_date": features_date,
        }).to_string()

    examples_section = ""
    if not self._is_followup_question(state):
        # Invoke EXAMPLE_CONVERSATION_DOC_TEMPLATE for each document and join with newlines
        fallback_example_date = "2025-01-01 00:00:00"
        example_support_cases = "\n".join(
            [ EXAMPLE_CONVERSATION_DOC_TEMPLATE.invoke({ "date": doc.date or fallback_example_date, "example": doc.content}).to_string() for doc in docs ]
        )
        examples_section = EXAMPLES_SECTION_TEMPLATE.invoke({
            "examples": example_support_cases
        }).to_string()

    user_context_json = state.get("user_context") or ""

    user_prompt = USER_PROMPT_TEMPLATE.invoke({
      "examples": examples_section,
      "features": features_section,
      "input": user_question,
      "user_context": user_context_json
    })

    messages = state.get("messages", []) + [HumanMessage(content=user_prompt.to_string())]

    prompt_template = ChatPromptTemplate([
      SystemMessage(content=SYSTEM_PROMPT),
      MessagesPlaceholder(variable_name="all_messages"),
    ])
    prompt: PromptValue = prompt_template.invoke({ "all_messages": messages })

    response = self.llm_model_dispatcher.invoke(prompt)

    question_language = state.get("question_language") or "de"
    final_answer = self.query_refiner.translate_message_if_needed(response.content, question_language)

    final_messages = messages + [AIMessage(content=final_answer)]

    Log.info(f"Returning final answer in Thread ID {self.thread_id}")
    return { "messages": final_messages, "answer": final_answer }
  
  def query(self, user_request: UserRequest, config: RunnableConfig) -> str:
    
    graph = self.build_workflow_graph()
    
    response = graph.invoke({
      "question": user_request.question,
      "request_params": user_request.request_params or {},
    }, config)

    return response["answer"]

  def _is_followup_question(self, state: State) -> bool:
    num_messages = state.get("messages", [])
    return len(num_messages) >= 2

  def _get_question_from_state(self, state: State) -> str:
      # return state.get("question"), True
    return state.get("question_refined")
  

  # def get_action(self, state: State) -> str:
  #   if state.get("public_event_id") is not None and len(state["public_event_id"]) > 0:
  #     return "fetch_public_event_info"
  #   return "no_additional_context"


  # def visualize_graph(self):
  #   display(Image(self.graph.get_graph().draw_mermaid_png()))