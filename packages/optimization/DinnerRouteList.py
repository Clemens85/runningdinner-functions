from typing import Dict, List, Optional
from pydantic import BaseModel

class Meal(BaseModel):
    id: str
    label: str

    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"{self.label}"

class GeocodingResult(BaseModel):
    lat: float
    lng: float
    resultType: str
    syncStatus: Optional[str] = None
    formattedAddress: Optional[str] = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"({self.lat}, {self.lng})"

class RouteOptimizationSettings(BaseModel):
    currentSumDistanceInMeters: float
    currentAverageDistanceInMeters: float
    ignoreMealAssignments: Optional[bool] = False
    minimumDistanceInMeters: Optional[int] = 0

class TeamsOnRoute(BaseModel):
    teamNumber: int
    teamId: str
    meal: Meal
    status: str
    geocodingResult: GeocodingResult
    clusterNumber: int
    teamsOnRoute: List["TeamsOnRoute"] = [] # Will always be empty in this context
    
    def __hash__(self):
        return hash((self.teamNumber, self.teamId))

    def __eq__(self, other):
        if not isinstance(other, (DinnerRoute, TeamsOnRoute)):
            return False
        return self.teamNumber == other.teamNumber and self.teamId == other.teamId

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Team({self.teamNumber}, {self.meal.label})"

class DinnerRoute(BaseModel):
    teamNumber: int
    teamId: str
    meal: Meal
    status: str
    geocodingResult: GeocodingResult
    clusterNumber: int
    teamsOnRoute: List[TeamsOnRoute] # List of teams which this host will visit on his route to take the other meals
    mealClass: Optional[str] = None
    originalIndex: Optional[int] = None
    
    def __hash__(self):
        return hash((self.teamNumber, self.teamId))

    def __eq__(self, other):
        if not isinstance(other, (DinnerRoute, TeamsOnRoute)):
            return False
        return self.teamNumber == other.teamNumber and self.teamId == other.teamId

    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"Team({self.teamNumber}, {self.meal.label})"

class DinnerRouteList(BaseModel):
    adminId: str
    optimizationId: str
    meals: List[Meal]
    dinnerRoutes: List[DinnerRoute]
    distanceMatrix: List[List[float]]
    clusterSizes: Dict[str, List[int]]
    optimizationSettings: RouteOptimizationSettings
