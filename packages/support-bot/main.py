import os
from dotenv import load_dotenv
from SupportBotSimple import SupportBotSimple
from langchain_core.runnables import RunnableConfig

from SupportBot import SupportBot
from UserRequest import UserRequest
from langgraph.checkpoint.memory import MemorySaver

load_dotenv(override=True)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

def main():

    question = "Unterstützt das Tool auch kürzeste Wegen bei den Routen? Wir veranstalten ein Event in Berlin und da ist es wichtig, dass man nicht vom einem Rand zum anderen Rand muss. Lg Jan"
    user_request = UserRequest(question=question, thread_id="1")

    config = new_configurable_from_user_request(user_request)
    response = request(user_request, config)

    user_request = UserRequest(question="In welcher Stadt war das Event zum ich dich vorhin befragt habe nochmal?", thread_id="1")
    config = new_configurable_from_user_request(user_request)
    response = request(user_request, config)


def request(user_request: UserRequest, config: RunnableConfig):
    support_bot = SupportBot()
    response = support_bot.query(user_request, config)
    return response

def new_configurable_from_user_request(user_request: UserRequest) -> RunnableConfig:
    return {"configurable": {
        "thread_id": user_request.thread_id
    }}

if __name__ == "__main__":
    main()
