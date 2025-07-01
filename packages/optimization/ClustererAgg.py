import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.metrics import pairwise_distances
import json

class ClustererAgg:
    def __init__(self, 
                 routes: pd.DataFrame, 
                 dist_matrix: np.ndarray, 
                 cluster_sizes: list
    ):
        """
        routes: DataFrame with route information (from DataProvider)
        dist_matrix: 2D numpy array with pairwise distances
        cluster_sizes: list of ints, only for 'balanced' algorithm
        """
        self.routes = routes.copy()  # Ensure we don't modify the original DataFrame
        self.dist_matrix = dist_matrix
        self.cluster_sizes = cluster_sizes

    def predict(self, distance_threshold=None, n_clusters=None):
        """
        n_clusters: Number of clusters to find (optional)
        distance_threshold: The linkage distance threshold above which clusters will not be merged (optional)
        Predict cluster labels based on the distance matrix and clustering parameters.
        """
        model = AgglomerativeClustering(
            metric='precomputed',
            linkage='complete',
            n_clusters=n_clusters,
            distance_threshold=distance_threshold
        )
        model.fit_predict(self.dist_matrix)
        labels = model.fit_predict(self.dist_matrix)
        self.routes['clusterNumber'] = labels
        return self.routes, labels
    
    def print_max_distances_per_cluster(self, optimizedRoutes, cluster_col='clusterNumber'):
        clusterNumbers = np.unique(optimizedRoutes[cluster_col])
        result = {}
        for cluster in clusterNumbers:
            if cluster == -1:
                continue  # -1 ist ggf. "Noise" bei DBSCAN
            indices = optimizedRoutes.index[optimizedRoutes[cluster_col] == cluster].tolist()
            if len(indices) < 2:
                print(f"Cluster {cluster}: nur 1 Element")
                result[cluster] = 0.0
                continue
            submatrix = self.dist_matrix[np.ix_(indices, indices)]
            max_dist = np.max(submatrix[np.triu_indices_from(submatrix, k=1)])
            result[cluster] = max_dist
            print(f"Cluster {cluster}: {len(indices)} Elemente, maximale Distanz: {max_dist:.2f}")
        return result

