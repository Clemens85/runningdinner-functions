from typing import Optional
from pydantic import BaseModel

class UserRequest(BaseModel):
    question: str
    url: Optional[str] = None
    thread_id: Optional[str] = None