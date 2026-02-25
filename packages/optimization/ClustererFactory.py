from Clusterer import Clusterer
from ClustererNewMealAssignments import ClustererNewMealAssignments
from RecursiveClustererNewMealAssignments import RecursiveClustererNewMealAssignments
from DataProvider import DataProvider
from DefaultClusterer import DefaultClusterer

def get_clusterer_instance(data_provider: DataProvider) -> Clusterer:
    if data_provider.get_optimization_settings().ignoreMealAssignments:
        return ClustererNewMealAssignments(data_provider=data_provider)
        # return RecursiveClustererNewMealAssignments(data_provider=data_provider)
    return DefaultClusterer(data_provider=data_provider)