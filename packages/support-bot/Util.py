from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

def to_openai_messages(chat_value) -> list:
    result = []
    for msg in chat_value.messages:
        if isinstance(msg, SystemMessage):
            role = "system"
        elif isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        else:
            raise ValueError(f"Unsupported message type: {type(msg)}")
        result.append({"role": role, "content": msg.content})
    return result