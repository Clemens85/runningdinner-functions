import os
from typing import List, Optional, Sequence

from langchain_core.language_models import BaseChatModel
from typing_extensions import Annotated, TypedDict
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from langgraph.graph import START, END, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from Prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, EXAMPLE_CONVERSATION_DOC_TEMPLATE
from UserRequest import UserRequest
from local_db.LocalChromaDbRepository import LocalChromaDbRepository
from pinecone_db.PineconeDbRepository import PineconeDbRepository

from memory.MemoryProvider import MemoryProvider
from Configuration import Configuration
from RequestParamsParser import RequestParamsParser

from api.RunningDinnerApi import RunningDinnerApi

# from IPython.display import Image, display

load_dotenv(override=True)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

OPENAI_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.2

class State(TypedDict, total=False):
  messages: Annotated[Sequence[BaseMessage], add_messages]
  docs: List[str]
  question: str
  answer: str
  request_params: dict[str, str]
  public_event_id: Optional[str]
  admin_id: Optional[str]
  
class SupportBot:
  
  def __init__(self, memory_provider: MemoryProvider, use_local_vector_db: bool = True):
    self.models: List[BaseChatModel] = []
    self.models.append(SupportBot.__init_openai())
    if use_local_vector_db:
      self.vector_db = LocalChromaDbRepository()
    else:
      self.vector_db = PineconeDbRepository()
    self.memory_provider = memory_provider

  @classmethod
  def __init_openai(cls) -> BaseChatModel:
    return init_chat_model(model_provider="openai", model=OPENAI_MODEL, temperature=TEMPERATURE)
  
  def build_workflow_graph(self):
    builder = StateGraph(state_schema=State)
    
    builder.add_node("parse_request_params", self.parse_request_params)
    builder.add_node("fetch_public_event_info", self.fetch_public_event_info)
    builder.add_node("retrieve_example_conversations", self.retrieve_example_conversations)
    builder.add_node("answer_with_context", self.answer_with_context)
    
    builder.add_edge(START, "parse_request_params")
    builder.add_conditional_edges(
      "parse_request_params", 
      self.get_action,
      {
        "no_additional_context": "retrieve_example_conversations",
        "fetch_public_event_info": "fetch_public_event_info"
      }
    )

    builder.add_edge("fetch_public_event_info", "retrieve_example_conversations")
    builder.add_edge("retrieve_example_conversations", "answer_with_context")
    builder.add_edge("answer_with_context", END)
    
    return builder.compile(checkpointer=self.memory_provider.get())
  
  def parse_request_params(self, state: State):
    request_params = state.get("request_params") or {}
    return RequestParamsParser.parse(request_params)

  def fetch_public_event_info(self, state: State, config: RunnableConfig):
    public_event_id = state["public_event_id"]
    configurable = Configuration.from_runnable_config(config)
    host = configurable.runningdinner_api_host

    try:
      api = RunningDinnerApi(host)
      public_event_info = api.get_public_event_info(public_event_id)
      return { "user_context": public_event_info }
    except Exception as e:
      print(f"Error fetching public event info: {e}")
      return {}

  def retrieve_example_conversations(self, state: State, config: RunnableConfig):

      question = state["question"]

      print ("*** CURRENT STATE ***")
      print(state)
      print("*** END CURRENT STATE ***")

      configurable = Configuration.from_runnable_config(config)
      k = configurable.max_similar_docs

      if state.get("docs") is not None and len(state.get("docs")) > 0:
        print(f"Already have {len(state['docs'])} documents in state, skipping retrieval.")
        return { "docs": []}

      print(f"--- RETRIEVE {k} SIMILAR CONTEXT DOCUMENTS ---")
      docs = self.vector_db.retrieve(query = question, top_k = k)
      return { "docs": docs }
  
  def answer_with_context(self, state: State):
    print("--- ANSWER WITH CONTEXT ---")

    user_question = state["question"]
    docs = state.get("docs") or []

    print(f"*** Question {user_question} has {len(docs)} documents as context.***")

    context_tmp = [ EXAMPLE_CONVERSATION_DOC_TEMPLATE.invoke({ "example": doc}).to_string() for doc in docs ]
    context = "\n".join(context_tmp)

    user_prompt = USER_PROMPT_TEMPLATE.invoke({
      "context": context,
      "input": user_question,
    })

    messages = state.get("messages", []) + [HumanMessage(content=user_prompt.to_string())]

    prompt_template = ChatPromptTemplate([
      SystemMessage(content=SYSTEM_PROMPT),
      MessagesPlaceholder(variable_name="all_messages"),
    ])
    prompt = prompt_template.invoke({ "all_messages": messages })

    model = self.models[0]
    response = model.invoke(prompt)

    final_messages = messages + [AIMessage(content=response.content)]
    # print ("\n*** STATE IS ***")
    # for msg in final_messages:
    #   print(msg.to_json())

    print ("\n*** MESSAGES ARE ***")
    for m in final_messages:
      m.pretty_print()
    print("\n*** END OF MESSAGES ***")

    return { "messages": final_messages, "answer": response.content }
  
  def query(self, user_request: UserRequest, config: RunnableConfig) -> str:
    
    graph = self.build_workflow_graph()
    
    response = graph.invoke({
      "question": user_request.question,
      "request_params": user_request.request_params or {},
    }, config)

    # print ("*** COMPLETE STATE IS ***")
    # print (graph.get_state(config))
    # print ("*** END OF COMPLETE STATE ***")
    return response["answer"]
  

  def get_action(self, state: State) -> str:
    if state.get("public_event_id") is not None and len(state["public_event_id"]) > 0:
      return "fetch_public_event_info"
    return "no_additional_context"


  # def visualize_graph(self):
  #   display(Image(self.graph.get_graph().draw_mermaid_png()))