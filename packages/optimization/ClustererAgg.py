from collections import Counter
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


    def __remove_excess_meal_classes(self, routes: pd.DataFrame, meal_class: str, cluster_indices: list, excess: int) -> list:
        """ Remove excess meal classes of a cluster.
        :param routes: DataFrame with route information
        :param meal_class: The meal class to remove excess of
        :param cluster_indices: List of indices in the current cluster
        :param excess: Number of excess meal classes to remove
        :return: Set of removed indices
        """
        affected_indices = [idx for idx in cluster_indices if routes.loc[idx, 'mealClass'] == meal_class]
        # Compute mean distance to other cluster members
        mean_dists = []
        for idx in affected_indices:
            others = list(set(cluster_indices) - {idx})
            if others:
                mean_dist = self.dist_matrix[idx, others].mean()
            else:
                mean_dist = 0
            mean_dists.append((mean_dist, idx))
        # Remove the ones with largest mean distance
        mean_dists.sort(reverse=True)
        removed_indices = set()
        for _, idx in mean_dists[:excess]:
            removed_indices.add(idx)
        return list(removed_indices)

    def __print_current_cluster_status(self, routes: pd.DataFrame, available_indices: set, cluster_labels_sorted: list):
        print("\n*** Current cluster status:***")
        print(f"Available indices: {available_indices}")
        for cluster_label in cluster_labels_sorted:
            cluster_indices = routes.index[routes['clusterNumber'] == cluster_label].tolist()
            meal_classes_current_cluster = routes.loc[cluster_indices, 'mealClass']
            current_counts = Counter(meal_classes_current_cluster)
            print(f"Cluster {cluster_label}:")
            print(f"Indices: {cluster_indices}")
            print(f"Meal classes: {meal_classes_current_cluster.tolist()}")
            print(f"Counts: {current_counts}\n")


    # In current implementation we expect clusters in routes exactly match the final number of clusters we need to create
    def predict_exact(self, cluster_templates: list[list[str]]):
        routes = self.routes.copy()
        cluster_labels_sorted = sorted(routes['clusterNumber'].unique())
        meal_classes = routes['mealClass'].unique()

        available_indices = set([])

        # Iterate over each cluster and remove excess meal classes
        for cluster_label in cluster_labels_sorted:
            cluster_indices = routes.index[routes['clusterNumber'] == cluster_label].tolist()
            meal_classes_current_cluster = routes.loc[cluster_indices, 'mealClass']
            current_counts = Counter(meal_classes_current_cluster)
            required_counts = Counter(cluster_templates[cluster_label])

            print(f"\nCluster {cluster_label}:")
            print(f"Current meal classes: {current_counts}")
            print(f"Required meal classes: {required_counts}")
            # Remove excess meal classes
            for meal_class in meal_classes:
                excess = current_counts[meal_class] - required_counts[meal_class]
                if excess > 0:
                    print(f"Cluster {cluster_label}: {meal_class} excess: {excess}")
                    removed_indices = self.__remove_excess_meal_classes(routes, meal_class, cluster_indices, excess)
                    print(f"Cluster {cluster_label}: Removed {excess} excess {meal_class} points")
                    # Remove removed_indices from cluster_indices and add them to available_indices
                    cluster_indices = [idx for idx in cluster_indices if idx not in removed_indices]
                    available_indices.update(removed_indices)
                    print (f"Removing cluster_label from {removed_indices}")
                    routes.loc[removed_indices, 'clusterNumber'] = -1  # Mark as removed or noise

        print("\n*** AFTER EXCEESS REMOVAL ***")
        self.__print_current_cluster_status(routes, available_indices, cluster_labels_sorted)

        # Now add missing meal classes to each cluster
        for cluster_label in cluster_labels_sorted:
            cluster_indices = routes.index[routes['clusterNumber'] == cluster_label].tolist()
            meal_classes_current_cluster = routes.loc[cluster_indices, 'mealClass']
            current_counts = Counter(meal_classes_current_cluster)
            required_counts = Counter(cluster_templates[cluster_label])
            
            # Add missing meal classes
            for meal_class in meal_classes:
                deficit = required_counts[meal_class] - current_counts[meal_class]
                if deficit > 0:
                    print(f"Cluster {cluster_label}: Need {deficit} more of {meal_class}.")
                    # Find nearest available points of this mealClass
                    candidates = [idx for idx in available_indices if routes.loc[idx, 'mealClass'] == meal_class]
                    print(f"Candidates for {meal_class} in cluster {cluster_label}: {candidates}")
                    # For each needed, pick the closest to the current cluster
                    for _ in range(deficit):
                        if not candidates:
                            raise ValueError(f"Not enough {meal_class} to fill cluster {cluster_label}")
                        # Compute distance to current cluster
                        dists = [self.dist_matrix[cand, cluster_indices].mean() for cand in candidates]

                        min_idx = np.argmin(dists)
                        chosen = candidates[min_idx]
                        print(f"Chosen index for cluster {cluster_label}: {chosen} with distance {dists[min_idx]:.2f}")
                        cluster_indices.append(chosen)
                        available_indices.remove(chosen)
                        routes.loc[chosen, 'clusterNumber'] = cluster_label
                        candidates.remove(chosen)

            print(f"\n*** After adding missing meal classes in cluster {cluster_label} ***")
            self.__print_current_cluster_status(routes, available_indices, cluster_labels_sorted)

        return routes, routes['clusterNumber'].values


    # def greedy_balance_clusters(self, cluster_templates):
    #     """
    #     routes: DataFrame with at least ['mealClass', ...]
    #     dist_matrix: numpy array, shape (n_samples, n_samples)
    #     cluster_labels: array-like, initial cluster assignment for each datapoint
    #     cluster_templates: list of lists, each inner list is the required mealClasses for that cluster
    #     """
    #     routes = self.routes.copy()
    #     uniqueClusterNumbersSorted = sorted(routes['clusterNumber'].unique())
    #     meal_classes = routes['mealClass'].unique()
    #     n_points = len(routes)

    #     # Build a lookup for available indices by mealClass
    #     # (0, 1, 2, ..., n_points-1)
    #     #range(n_points)
    #     available_indices = set([])
    #     # cluster_indices is a dict, mapping each cluster label to the set of DataFrame indices belonging to that cluster.
    #     # Example: {0: {0, 2}, 1: {1, 3}, 2: {4}}
    #     cluster_indices = {label: set(routes.index[routes['clusterNumber'] == label]) for label in uniqueClusterNumbersSorted}
    #     print (cluster_indices)

    #     # *** TODO: Change following
    #     # - remove firstly excesses over ALL clusters
    #     #     - When removing excess, remove the farthest points from the cluster center    
    #     # - then add missing mealClasses to each cluster (nearest available points like in the original algorithm)
    #     # - the missing mealclasses must however be fetched "globally" from the available indices, not just from the current cluster indicies (but should firstly be taken from the available indicies)

    #     # For each cluster, enforce the template
    #     for cluster_idx, template in enumerate(cluster_templates):
    #         required = Counter(template)
    #         team_indices_current_cluster = list(cluster_indices[cluster_idx])
    #         meal_classes_current_cluster = routes.loc[team_indices_current_cluster, 'mealClass']
    #         current = Counter(meal_classes_current_cluster)

    #         print(f"\n********* CLUSTER {cluster_idx} *********")
    #         print(f"Current cluster {cluster_idx} has {len(cluster_indices[cluster_idx])} points.")
    #         print(f"Current meal classes in cluster {cluster_idx}:\n{meal_classes_current_cluster}")
    #         print(f"Required meal classes for cluster {cluster_idx}: {required}")
    #         print(f"Current meal classes count in cluster {cluster_idx}: {current}")

    #         # Remove excess
    #         for mealClass in meal_classes:
    #             excess = current[mealClass] - required[mealClass]
    #             print(f"Cluster {cluster_idx}: {mealClass} excess: {excess}")
    #             if excess > 0:
    #                 # Remove farthest points of this mealClass from the cluster center
    #                 indices = [idx for idx in cluster_indices[cluster_idx] if routes.loc[idx, 'mealClass'] == mealClass]
    #                 # Compute mean distance to other cluster members
    #                 mean_dists = []
    #                 for idx in indices:
    #                     # other shall not contain the idx itself
    #                     others = list(cluster_indices[cluster_idx] - {idx})
    #                     if others:
    #                         mean_dist = self.dist_matrix[idx, others].mean()
    #                     else:
    #                         mean_dist = 0
    #                     mean_dists.append((mean_dist, idx))
    #                 # Remove the ones with largest mean distance
    #                 mean_dists.sort(reverse=True)
    #                 for _, idx in mean_dists[:excess]:
    #                     cluster_indices[cluster_idx].remove(idx)
    #                     available_indices.add(idx)
    #                 print (f"Cluster {cluster_idx}: Removed {excess} excess {mealClass} points. \nRemaining: {len(cluster_indices[cluster_idx])}")


    #         print(f"*** Updated cluster indices after removal: {cluster_indices}***\n")

    #         print('\n+++ ADDITION +++')
    #         # Add missing
    #         for mealClass in meal_classes:
    #             deficit = required[mealClass] - Counter(routes.loc[list(cluster_indices[cluster_idx]), 'mealClass'])[mealClass]
    #             if deficit > 0:
    #                 print(f"Cluster {cluster_idx}: Need {deficit} more of {mealClass}.")
    #                 print("Available indices:", available_indices)
    #                 # Find nearest available points of this mealClass
    #                 candidates = [idx for idx in available_indices if routes.loc[idx, 'mealClass'] == mealClass]
    #                 print(f"Candidates for {mealClass} in cluster {cluster_idx}: {candidates}")
    #                 # For each needed, pick the closest to the current cluster
    #                 for _ in range(deficit):
    #                     if not candidates:
    #                         raise ValueError(f"Not enough {mealClass} to fill cluster {cluster_idx}")
    #                     # Compute distance to current cluster
    #                     if cluster_indices[cluster_idx]:
    #                         dists = [self.dist_matrix[cand, list(cluster_indices[cluster_idx])].mean() for cand in candidates]
    #                         # print(f"Distances for candidates in cluster {cluster_idx}: {dists}")
    #                     else:
    #                         dists = [0 for _ in candidates]
    #                     min_idx = np.argmin(dists)
    #                     chosen = candidates[min_idx]
    #                     print(f"Chosen index for cluster {cluster_idx}: {chosen} with distance {dists[min_idx]:.2f}")
    #                     cluster_indices[cluster_idx].add(chosen)
    #                     available_indices.remove(chosen)
    #                     candidates.remove(chosen)

    #                 print(f"*** Updated cluster indices after addition: {cluster_indices}***\n")

    #     print("\n-----------\n")

    #     # Build final assignments
    #     final_labels = np.empty(n_points, dtype=int)
    #     for new_idx, (cluster_number_label, indices) in enumerate(cluster_indices.items()):
    #         for idx in indices:
    #             final_labels[idx] = cluster_number_label

    #     print(f"Final cluster labels: {final_labels}")
    #     routes['clusterNumber'] = final_labels
    #     return routes, final_labels
