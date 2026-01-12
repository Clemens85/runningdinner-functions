from pydantic import BaseModel
from ProposalFileType import ProposalFileType

class ExampleMessage(BaseModel):
    message: str
    event_description: str
    type: ProposalFileType