
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Meal:
    id: str
    label: str

@dataclass
class TeamsOnRoute:
    teamNumber: int
    teamId: str
    meal: Meal
    status: str
    lat: float
    lng: float
    geocodingResult: str
    clusterNumber: int
    teamsOnRoute: List["TeamsOnRoute"] # Will always be empty in this context

@dataclass
class DinnerRoute:
    teamNumber: int
    teamId: str
    meal: Meal
    status: str
    lat: float
    lng: float
    geocodingResult: str
    clusterNumber: int
    teamsOnRoute: List[TeamsOnRoute]
    mealClass: Optional[str] = None
    originalIndex: Optional[int] = None

@dataclass
class DinnerRouteList:
    adminId: str
    optimizationId: str
    dinnerRoutes: List[DinnerRoute]
    distanceMatrix: List[List[float]]
    clusterSizes: Dict[str, List[int]]

