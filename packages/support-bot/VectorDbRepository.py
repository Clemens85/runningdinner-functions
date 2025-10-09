from abc import ABC, abstractmethod
from typing import List
from SupportDocument import SupportDocument

class VectorDbRepository(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k=2) -> List[SupportDocument]:
        pass