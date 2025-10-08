import os
from typing import Sequence
from typing_extensions import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

OPENAI_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.2

class State(TypedDict):
  messages: Annotated[Sequence[BaseMessage], add_messages]
  language: str

class SupportBotSimple:
  
  def __init__(self, configuration: RunnableConfig):
    load_dotenv(override=True)
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
    # Use internal ChatOpenAI wrapper instead of langchain meta package
    from llm.ChatOpenAI import ChatOpenAI
    self.models = [ChatOpenAI(model=OPENAI_MODEL, temperature=TEMPERATURE)]
    
    self.workflow = self.__init_workflow_graph()
    self.configuration = configuration
    
    self.prompt_template = self.__init_prompt_template()
  
  def __init_openai(self):
    # Deprecated: kept for backward compatibility if referenced elsewhere
    from llm.ChatOpenAI import ChatOpenAI
    return ChatOpenAI(model=OPENAI_MODEL, temperature=TEMPERATURE)
  
  def __init_workflow_graph(self):
    workflow = StateGraph(state_schema=State)
    workflow.add_edge(START, "query")
    workflow.add_node("query", self.call_model)
    
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
  
  
  def call_model(self, state: State):
    model = self.__get_model()
    
    prompt = self.prompt_template.invoke(state)
    print(f"Invoking model with prompt: {prompt}")
    
    response = model.invoke(prompt)
    print (f"Got response: {response}")
    return {"messages": response}
    
  
  def query(self, user_message: str):
    input =  [HumanMessage(user_message)]
    
    language = self.configuration["configurable"]["language"]
    print("Got configurable language: " + language)
    
    response = self.workflow.invoke({ "messages": input, "language": language }, self.configuration)
    return response["messages"][-1]
  
  def __get_model(self):
    return self.models[0]
  
  def __init_prompt_template(self):
    system_prompt = """You are a helpful assistant for RunningDinner organizers. 
                      You know everything about RunningDinner events and can help with questions about organizing, rules, and best practices.
                      You can also remember the organizer's name and details from earlier in the conversation.
                      If you don't know the answer, just say you don't know. Do not make up answers.
                      Always be polite and professional.
                      Answer the questions in this language {language}.
                      Your responses should be concise and to the point.
                      """
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return prompt_template
    