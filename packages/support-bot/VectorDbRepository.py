from abc import ABC, abstractmethod
from typing import Tuple
from langchain_core.documents import Document

class VectorDbRepository(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k=2) -> Tuple[str, list[Document]]:
        pass