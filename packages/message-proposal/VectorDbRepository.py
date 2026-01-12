from abc import ABC, abstractmethod
from typing import List
from DocumentVectorizable import DocumentVectorizable

class VectorDbRepository(ABC):
    @abstractmethod
    def find_similar_docs(self, query: str, top_k: int = 3) -> List[DocumentVectorizable]:
        pass

    @abstractmethod
    def add_document(self, doc_id: str, document: DocumentVectorizable):
        pass

    @abstractmethod
    def reset(self):
        pass