from pydantic import BaseModel

class DetectedLanguage(BaseModel):
    name: str
    iso_code: str
