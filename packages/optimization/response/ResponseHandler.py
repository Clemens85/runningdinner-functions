from abc import ABC, abstractmethod
from typing import Dict

class ResponseHandler(ABC):
    @abstractmethod
    def send(self, json_payload: str, finished_event: Dict[str, any]):
        pass