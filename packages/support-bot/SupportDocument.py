from typing import Optional

from pydantic import BaseModel

class SupportDocument(BaseModel):
    content: str
    date: Optional[str]
    support_type: Optional[str]