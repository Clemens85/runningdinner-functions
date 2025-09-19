from typing import Optional
from pydantic import BaseModel

URL_KEY = "url"

class UserRequest(BaseModel):
    question: str
    request_params: Optional[dict[str, str]] = None
    thread_id: Optional[str] = None