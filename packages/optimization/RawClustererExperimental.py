from typing import List, Tuple

from sklearn.cluster import AgglomerativeClustering

from DataProvider import DataProvider
from DinnerRouteList import DinnerRoute

class RawClustererExperimental:
    def __init__(self, data_provider: DataProvider):
        self.routes = data_provider.get_routes()
        self.dist_matrix = data_provider.get_distance_matrix()
        self.cluster_sizes = data_provider.get_cluster_sizes()
        self.cluster_templates = data_provider.get_cluster_template()
        self.data_provider = data_provider

    def predict(self, n_clusters: int = None, distance_threshold: int = None) -> Tuple[List[DinnerRoute], List[int]]:

        if n_clusters is None and distance_threshold is None:
            n_clusters = len(self.cluster_sizes)

        model = AgglomerativeClustering(
            metric='precomputed',
            linkage='complete',
            n_clusters=n_clusters,
            distance_threshold=distance_threshold
        )
        labels = model.fit_predict(self.dist_matrix)
        for route, label in zip(self.routes, labels):
            route.clusterNumber = label
        return self.routes, labels