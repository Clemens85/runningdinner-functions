from collections import Counter
from typing import List
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from DataProvider import DataProvider
from DinnerRouteList import DinnerRoute

class Clusterer:
    def __init__(self, 
                 data_provider: DataProvider
    ):
        """
        Given DataProvider instance, initializes the Clusterer with following attributes:
        routes: List with route information (from DataProvider)
        dist_matrix: 2D numpy array with pairwise distances
        cluster_sizes: list of ints, indicating the original number of clusters and the value of each element indicates the size of the cluster
        """
        self.routes = data_provider.get_routes()
        self.dist_matrix = data_provider.get_distance_matrix()
        self.cluster_sizes = data_provider.get_cluster_sizes()
        self.cluster_templates = data_provider.get_cluster_template()

    def __predict_draft(self, n_clusters=None):
        """
        n_clusters: Number of clusters to find (optional)
        Predict cluster labels based on the distance matrix and clustering parameters.
        """
        if n_clusters is None:
            n_clusters = len(self.cluster_sizes)
            
        model = AgglomerativeClustering(
            metric='precomputed',
            linkage='complete',
            n_clusters=n_clusters,
        )
        labels = model.fit_predict(self.dist_matrix)
        for route, label in zip(self.routes, labels):
            route.clusterNumber = label
        return self.routes, labels
    
    def print_max_distances_per_cluster(self):
        cluster_labels_sorted = sorted({route.clusterNumber for route in self.routes})
        result = {}
        for cluster_label in cluster_labels_sorted:
            if cluster_label == -1:
                continue  # -1 ist ggf. "Noise" bei DBSCAN
            
            indices_of_cluster = [route.originalIndex for route in self.routes if route.clusterNumber == cluster_label]
            if len(indices_of_cluster) < 2:
                print(f"Cluster {cluster_label}: nur 1 Element")
                result[cluster_label] = 0.0
                continue
            submatrix = self.dist_matrix[np.ix_(indices_of_cluster, indices_of_cluster)]
            max_dist = np.max(submatrix[np.triu_indices_from(submatrix, k=1)])
            result[cluster_label] = max_dist
            print(f"Cluster {cluster_label}: {len(indices_of_cluster)} Elemente, maximale Distanz: {max_dist:.2f}")
        return result


    def __remove_excess_meal_classes(self, routes_of_cluster: List[DinnerRoute], meal_class: str, excess: int) -> list:
        """ Calculate indices to be removed for excess meal classes of a cluster.
        :param routes_of_cluster: List fo all routes in current cluster
        :param meal_class: The meal class to remove excess of
        :param excess: Number of excess meal classes to remove
        :return: Set of indices to remove
        """
        meal_class_indices = [route.originalIndex for route in routes_of_cluster if route.mealClass == meal_class]
        all_cluster_indices = set([route.originalIndex for route in routes_of_cluster])

        # Compute mean distance to other cluster members
        mean_dists = []
        for idx in meal_class_indices:
            others = list(all_cluster_indices - {idx})
            if others:
                mean_dist = self.dist_matrix[idx, others].mean()
            else:
                mean_dist = 0
            mean_dists.append((mean_dist, idx))
        # Remove the ones with largest mean distance
        mean_dists.sort(reverse=True)
        indices_to_remove = set()
        for _, idx in mean_dists[:excess]:
            indices_to_remove.add(idx)
        return list(indices_to_remove)

    def __print_current_cluster_status(self, available_indices: set, cluster_labels_sorted: list):
        print("\n*** Current cluster status:***")
        print(f"Available indices: {available_indices}")
        for cluster_label in cluster_labels_sorted:
            indices_of_cluster = [route.originalIndex for route in self.routes if route.clusterNumber == cluster_label]
            meal_classes_current_cluster = [route.mealClass for route in self.routes if route.clusterNumber == cluster_label]
            current_counts = Counter(meal_classes_current_cluster)
            print(f"Cluster {cluster_label}:")
            print(f"Indices: {indices_of_cluster}")
            print(f"Meal Class Counts: {current_counts}\n")


    def predict(self):
        
        self.__predict_draft() # This modifies our routes and set predicted cluster labels

        cluster_labels_sorted = sorted({route.clusterNumber for route in self.routes})
        meal_classes = sorted({route.mealClass for route in self.routes})

        available_indices = set([])

        # Iterate over each cluster and remove excess meal classes
        for cluster_label in cluster_labels_sorted:
            
            routes_of_cluster = [route for route in self.routes if route.clusterNumber == cluster_label]
            meal_classes_current_cluster = [route.mealClass for route in routes_of_cluster]

            current_counts = Counter(meal_classes_current_cluster)
            required_counts = Counter(self.cluster_templates[cluster_label])

            print(f"\nCluster {cluster_label}:")
            print(f"Current meal classes: {current_counts}")
            print(f"Required meal classes: {required_counts}")
            # Remove excess meal classes
            for meal_class in meal_classes:
                excess = current_counts[meal_class] - required_counts[meal_class]
                if excess > 0:
                    print(f"Cluster {cluster_label}: {meal_class} excess: {excess}")
                    removed_indices = self.__remove_excess_meal_classes(routes_of_cluster, meal_class, excess)
                    available_indices.update(removed_indices)
                    print (f"Removing indices {removed_indices} from cluster {cluster_label}")
                    for route in routes_of_cluster:
                        if route.originalIndex in removed_indices:
                            route.clusterNumber = -1 # Mark as removed

                    #routes.loc[removed_indices, 'clusterNumber'] = -1  # Mark as removed or noise

        print("\n*** AFTER EXCEESS REMOVAL ***")
        self.__print_current_cluster_status(available_indices, cluster_labels_sorted)

        # Now add missing meal classes to each cluster
        for cluster_label in cluster_labels_sorted:
            routes_of_cluster = [route for route in self.routes if route.clusterNumber == cluster_label]
            meal_classes_current_cluster = [route.mealClass for route in routes_of_cluster]
            indices_of_cluster = [route.originalIndex for route in routes_of_cluster]

            current_counts = Counter(meal_classes_current_cluster)
            required_counts = Counter(self.cluster_templates[cluster_label])

            # Add missing meal classes
            for meal_class in meal_classes:
                deficit = required_counts[meal_class] - current_counts[meal_class]
                if deficit > 0:
                    print(f"Cluster {cluster_label}: Need {deficit} more of {meal_class}.")
                    # Find nearest available points of this mealClass
                    candidate_indices = [idx for idx in available_indices if self.routes[idx].mealClass == meal_class]
                    print(f"Candidates for {meal_class} in cluster {cluster_label}: {candidate_indices}")
                    # For each needed, pick the closest to the current cluster
                    for _ in range(deficit):
                        if not candidate_indices:
                            raise ValueError(f"Not enough {meal_class} to fill cluster {cluster_label}")
                        # Compute distance to current cluster
                        dists = [self.dist_matrix[cand, indices_of_cluster].mean() for cand in candidate_indices]

                        min_idx = np.argmin(dists)
                        chosen_index = candidate_indices[min_idx]
                        print(f"Chosen index for cluster {cluster_label}: {chosen_index} with distance {dists[min_idx]:.2f}")
                        indices_of_cluster.append(chosen_index)
                        # Update the route with the cluster label
                        self.routes[chosen_index].clusterNumber = cluster_label
                        available_indices.remove(chosen_index)
                        candidate_indices.remove(chosen_index)

            print(f"\n*** After adding missing meal classes in cluster {cluster_label} ***")
            self.__print_current_cluster_status(available_indices, cluster_labels_sorted)

        final_cluster_labels = [route.clusterNumber for route in self.routes]
        return self.routes, final_cluster_labels
