from pydantic import BaseModel


class ModelConfiguration(BaseModel):
  model_name: str
  temperature: float