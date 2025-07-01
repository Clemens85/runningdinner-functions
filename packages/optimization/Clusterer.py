import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.metrics import pairwise_distances
import json

class Clusterer:
    def __init__(self, 
                 routes: pd.DataFrame, 
                 dist_matrix: np.ndarray, 
                 algorithm: str = "agglomerative",
                 n_clusters: int = None, 
                 distance_threshold: float = None,
                 cluster_sizes: list = None):
        """
        routes: DataFrame with route information (from DataProvider)
        dist_matrix: 2D numpy array with pairwise distances
        n_clusters: Number of clusters to find (optional)
        distance_threshold: The linkage distance threshold above which clusters will not be merged (optional)
        algorithm: 'agglomerative', 'kmeans', 'dbscan', 'balanced'
        cluster_sizes: list of ints, only for 'balanced' algorithm
        """
        self.routes = routes.copy()  # Ensure we don't modify the original DataFrame
        self.dist_matrix = dist_matrix
        self.algorithm = algorithm.lower()
        self.n_clusters = n_clusters
        self.distance_threshold = distance_threshold
        self.cluster_sizes = cluster_sizes

    def cluster(self):
        if self.algorithm == "agglomerative":
            model = AgglomerativeClustering(
                metric='precomputed',
                linkage='average',
                n_clusters=self.n_clusters,
                distance_threshold=self.distance_threshold
            )
            labels = model.fit_predict(self.dist_matrix)
        elif self.algorithm == "dbscan":
            model = DBSCAN(metric='precomputed', eps=4500)
            labels = model.fit_predict(self.dist_matrix)
        elif self.algorithm == "kmeans":
            coords = self.routes[['lat', 'lng']].values
            model = KMeans(n_clusters=self.n_clusters)
            labels = model.fit_predict(coords)
        elif self.algorithm == "balanced":
            if self.cluster_sizes is None:
                raise ValueError("Für 'balanced' muss cluster_sizes übergeben werden!")
            coords = self.routes[['lat', 'lng']].values
            labels = self.balanced_assignment(coords, self.cluster_sizes)
        else:
            raise ValueError(f"Unbekannter Algorithmus: {self.algorithm}")
        self.routes['clusterNumber'] = labels
        return self.routes, labels

    @staticmethod
    def balanced_assignment(coords, cluster_sizes):
        n_clusters = len(cluster_sizes)
        n_samples = coords.shape[0]
        rng = np.random.default_rng()
        centers_idx = rng.choice(n_samples, n_clusters, replace=False)
        centers = coords[centers_idx]
        dists = pairwise_distances(coords, centers)
        clusters = [[] for _ in range(n_clusters)]
        assigned = np.zeros(n_samples, dtype=bool)
        for size, cluster_id in zip(cluster_sizes, range(n_clusters)):
            idx = np.argsort(dists[:, cluster_id])
            count = 0
            for i in idx:
                if not assigned[i]:
                    clusters[cluster_id].append(i)
                    assigned[i] = True
                    count += 1
                    if count == size:
                        break
        labels = np.empty(n_samples, dtype=int)
        for cluster_id, members in enumerate(clusters):
            for i in members:
                labels[i] = cluster_id
        return labels

    def print_max_distances_per_cluster(self, routes_df, dist_matrix, cluster_col='clusterNumber'):
        for cluster in np.unique(routes_df[cluster_col]):
            if cluster == -1:
                continue  # -1 ist ggf. "Noise" bei DBSCAN
            indices = routes_df.index[routes_df[cluster_col] == cluster].tolist()
            if len(indices) < 2:
                print(f"Cluster {cluster}: nur 1 Element")
                continue
            submatrix = dist_matrix[np.ix_(indices, indices)]
            max_dist = np.max(submatrix[np.triu_indices_from(submatrix, k=1)])
            print(f"Cluster {cluster}: {len(indices)} Elemente, maximale Distanz: {max_dist:.2f}")