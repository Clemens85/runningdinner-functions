from typing import Optional
from pydantic import BaseModel

PAGE_NAME_KEY = "page_name"
PUBLIC_EVENT_REGISTRATIONS_KEY = "public_event_registrations"

class UserRequest(BaseModel):
    question: str
    request_params: Optional[dict[str, str]] = None
    thread_id: Optional[str] = None