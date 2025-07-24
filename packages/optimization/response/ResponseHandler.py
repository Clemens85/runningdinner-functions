from abc import ABC, abstractmethod

class ResponseHandler(ABC):
    @abstractmethod
    def send(self, json_string: str):
        pass