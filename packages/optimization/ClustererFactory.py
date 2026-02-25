from Clusterer import Clusterer
from ClustererNewMealAssignmentsV2 import ClustererNewMealAssignmentsV2
from DataProvider import DataProvider
from DefaultClusterer import DefaultClusterer

def get_clusterer_instance(data_provider: DataProvider) -> Clusterer:
    if data_provider.get_optimization_settings().ignoreMealAssignments:
        return ClustererNewMealAssignmentsV2(data_provider=data_provider)
    return DefaultClusterer(data_provider=data_provider)