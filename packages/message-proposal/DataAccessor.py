from abc import ABC, abstractmethod

class DataAccessor(ABC):

    @abstractmethod
    def load_string(self, storage_path: str) -> str:
        pass

    @abstractmethod
    def write_string_to_path(self, content: str, storage_path: str):
        pass
