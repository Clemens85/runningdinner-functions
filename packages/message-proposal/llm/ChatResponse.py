from pydantic import BaseModel

class ChatResponse(BaseModel):
    content: str
    is_structured: bool = False