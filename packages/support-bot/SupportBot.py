import os
import re
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
from langchain_core.documents import Document

from Prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, EXAMPLE_CONVERSATION_DOC_TEMPLATE
from UserRequest import UserRequest
from local_db.LocalChromaDbRepository import LocalChromaDbRepository

from memory.MemoryProvider import MemoryProvider
from Configuration import Configuration

# from IPython.display import Image, display

load_dotenv(override=True)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

OPENAI_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.2

class State(TypedDict, total=False):
  messages: Annotated[Sequence[BaseMessage], add_messages]
  docs: List[Document]
  question: str
  answer: str
  url: Optional[str]
  public_event_id: Optional[str]
  admin_id: Optional[str]
  
class SupportBot:
  
  def __init__(self):    
    self.models: List[BaseChatModel] = []
    self.models.append(SupportBot.__init_openai())
    self.vector_db = LocalChromaDbRepository()

  @classmethod
  def __init_openai(cls) -> BaseChatModel:
    return init_chat_model(model_provider="openai", model=OPENAI_MODEL, temperature=TEMPERATURE)
  
  def build_workflow_graph(self):
    builder = StateGraph(state_schema=State)
    
    builder.add_node("refine_query", self.refine_query)
    builder.add_node("retrieve_context", self.retrieve_context)
    builder.add_node("fetch_public_event_info", self.fetch_public_event_info)
    builder.add_node("answer_with_context", self.answer_with_context)
    
    builder.add_edge(START, "refine_query")
    builder.add_edge("refine_query", "retrieve_context")
    builder.add_conditional_edges(
      "retrieve_context", 
      self.get_action,
      {
        "answer_with_context": "answer_with_context",
        "fetch_public_event_info": "fetch_public_event_info"
      }
    )
    builder.add_edge("fetch_public_event_info", "answer_with_context")  # Loop back after fetching info
    builder.add_edge("answer_with_context", END)
    
    memory_provider = MemoryProvider()
    return builder.compile(checkpointer=memory_provider.get())
  
  def refine_query(self, state: State):

    print(f"--- REFINE QUERY ---")
    url = state["url"]
    
    public_event_id = None
    admin_id = None
    
    if url:
      match = re.search(r"/running-dinner-events/([^/]+)", url)
      if match:
        public_event_id = match.group(1)
   
    return { "public_event_id": public_event_id, "admin_id": admin_id }
  
  def retrieve_context(self, state: State, config: RunnableConfig):

      question = state["question"]

      print ("*** CURRENT STATE ***")
      print(state)
      print("*** END CURRENT STATE ***")

      configurable = Configuration.from_runnable_config(config)
      k = configurable.max_similar_docs

      if state.get("docs") is not None and len(state.get("docs")) > 0:
        print(f"Already have {len(state['docs'])} documents in state, skipping retrieval.")
        return {}

      print(f"--- RETRIEVE {k} SIMILAR CONTEXT DOCUMENTS ---")
      docs = self.vector_db.retrieve(query = question, k = k)
      return { "docs": docs }
  
  def answer_with_context(self, state: State):
    print("--- ANSWER WITH CONTEXT ---")

    user_question = state["question"]
    docs = state["docs"]

    print(f"*** Question {user_question} has {len(docs)} documents as context.***")

    context_tmp = [ EXAMPLE_CONVERSATION_DOC_TEMPLATE.invoke({ "example": doc.page_content}).to_string() for doc in docs ]
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
    
    question = user_request.question
    url = user_request.url

    graph = self.build_workflow_graph()
    
    response = graph.invoke({
      "question": question,
      "url": url
    }, config)

    # print ("*** COMPLETE STATE IS ***")
    # print (graph.get_state(config))
    # print ("*** END OF COMPLETE STATE ***")
    return response["answer"]
  
  def fetch_public_event_info(self, state: State):
    print(f"--- FETCH PUBLIC EVENT INFO --- with state {state}")
    public_event_id = state["public_event_id"]
    # TODO fetch more info about the event if necessary
    print(f"Fetching more info about public event id: {public_event_id}")
    return state
  

  def get_action(self, state: State) -> str:
    if state.get("public_event_id") is not None:
      return "fetch_public_event_info"
    return "answer_with_context"


  # def visualize_graph(self):
  #   display(Image(self.graph.get_graph().draw_mermaid_png()))