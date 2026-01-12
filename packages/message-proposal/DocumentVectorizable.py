from pydantic import BaseModel

class DocumentVectorizable(BaseModel):
    id: str
    page_content: str
    type: str
    admin_id: str
    source_path: str
    metadata: dict