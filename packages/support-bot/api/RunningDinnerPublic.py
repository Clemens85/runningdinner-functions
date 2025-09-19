from typing import Optional
from pydantic import BaseModel

class PublicSettingsTO(BaseModel):
    title: str
    description: str
    publicContactName: str
    publicContactEmail: str
    publicContactMobileNumber: Optional[str]
    publicDinnerId: str

class RunningDinnerPublicTO(BaseModel):
    city: str
    date: str
    zip: str
    publicSettings: PublicSettingsTO