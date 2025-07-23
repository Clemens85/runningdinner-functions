from typing import Dict, List, Optional
from pydantic import BaseModel

class Meal(BaseModel):
    id: str
    label: str

    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"{self.label}"

class TeamsOnRoute(BaseModel):
    teamNumber: int
    teamId: str
    meal: Meal
    status: str
    lat: float
    lng: float
    geocodingResult: str
    clusterNumber: int
    teamsOnRoute: List["TeamsOnRoute"] = [] # Will always be empty in this context
    
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Team({self.teamNumber}, {self.meal.label})"

class DinnerRoute(BaseModel):
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
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        visits = [str(team_on_route) for team_on_route in self.teamsOnRoute]
        visits_str = ", ".join(visits) if visits else "[]"
        # return f"Team({self.teamNumber}, {self.meal.label} (--> {visits_str}))"
        return f"Team({self.teamNumber}, {self.meal.label})"

class DinnerRouteList(BaseModel):
    adminId: str
    optimizationId: str
    meals: List[Meal]
    dinnerRoutes: List[DinnerRoute]
    distanceMatrix: List[List[float]]
    clusterSizes: Dict[str, List[int]]
