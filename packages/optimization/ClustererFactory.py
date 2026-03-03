from Clusterer import Clusterer
from DefaultClusterer import DefaultClusterer
from DataProvider import DataProvider

def get_clusterer_instance(data_provider: DataProvider) -> Clusterer:
    # if data_provider.get_optimization_settings().ignoreMealAssignments:
    #     return LegacyClusterer(data_provider=data_provider)
    return DefaultClusterer(data_provider=data_provider)