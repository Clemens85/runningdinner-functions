from abc import ABC, abstractmethod
from typing import Tuple, List

from DinnerRouteList import DinnerRoute

class Clusterer(ABC):
    @abstractmethod
    def predict(self) -> Tuple[List[DinnerRoute], List[int]]:
        pass