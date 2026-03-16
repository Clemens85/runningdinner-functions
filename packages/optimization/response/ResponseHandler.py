from abc import ABC, abstractmethod
from response.OptimizationEvent import OptimizationEvent


class ResponseHandler(ABC):
    @abstractmethod
    def send(self, json_payload: str, finished_event: OptimizationEvent):
        pass