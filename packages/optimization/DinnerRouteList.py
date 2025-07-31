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

class TeamsOnRoute(BaseModel):
    teamNumber: int
    teamId: str
    meal: Meal
    status: str
    geocodingResult: GeocodingResult
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
    geocodingResult: GeocodingResult
    clusterNumber: int
    teamsOnRoute: List[TeamsOnRoute]
    mealClass: Optional[str] = None
    originalIndex: Optional[int] = None
    
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
