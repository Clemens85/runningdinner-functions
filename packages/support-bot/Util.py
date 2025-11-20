import os

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompt_values import PromptValue


def to_openai_messages(chat_value: PromptValue) -> list:
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

def to_gemini_messages(chat_value: PromptValue) -> tuple[str | None, list]:
    """
    Convert PromptValue to Gemini format.
    Returns (system_instruction, messages_list)
    Gemini uses 'user' and 'model' roles, and system messages are handled separately.
    """
    system_instruction = None
    result = []
    for msg in chat_value.messages:
        if isinstance(msg, SystemMessage):
            # Gemini handles system messages separately as system_instruction
            system_instruction = msg.content
        elif isinstance(msg, HumanMessage):
            result.append({"role": "user", "parts": [{"text": msg.content}]})
        elif isinstance(msg, AIMessage):
            result.append({"role": "model", "parts": [{"text": msg.content}]})
        else:
            raise ValueError(f"Unsupported message type: {type(msg)}")
    return system_instruction, result

def is_running_on_lambda():
    return "AWS_LAMBDA_FUNCTION_NAME" in os.environ