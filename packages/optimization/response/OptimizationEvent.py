from typing import Optional
from pydantic import BaseModel


class OptimizationEvent(BaseModel):
    adminId: str
    optimizationId: str
    errorMessage: Optional[str] = None
