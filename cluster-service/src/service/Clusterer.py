import numpy as np
from geopy.distance import geodesic
from src.model.LocationDict import LocationDict
from sklearn import cluster

class Clusterer:
    def __init__(self, locations: LocationDict):
        """
        Initializes the cluster object with the given locations.
        Precomputes the distance matrix.
        :param locations: Collection of locations given as object of type LocationDict.
        """
        N = len(locations)
        self.metric : np.array = np.empty(shape=(N, N))
        self.labels : list = N * [None]

        for row_idx, row_id in enumerate(locations):
            for col_idx, col_id in enumerate(locations):
                self.metric[row_idx, col_idx] = geodesic((locations[row_id].lat, locations[row_id].lon), (locations[col_id].lat, locations[col_id].lon)).meters

    def predict(self, threshold: float):
        """
        Performs agglomerative clustering on the location data
        """
        clusterer = cluster.AgglomerativeClustering(metric='precomputed', linkage='complete', distance_threshold=threshold, n_clusters=None)
        self.labels = clusterer.fit_predict(self.metric)

    def labels(self):
        """
        :return: Labels for each location in the collection this object has been initialized with. Preserved order.
        """
        return self.labels