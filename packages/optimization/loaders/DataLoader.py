from abc import ABC, abstractmethod

class DataLoader(ABC):
    @abstractmethod
    def load_json_string(self) -> str:
        pass