from pydantic import BaseModel

URL_KEY = "url"

class UserResponse(BaseModel):
    answer: str
    thread_id: str