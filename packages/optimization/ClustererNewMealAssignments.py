from Clusterer import Clusterer
from collections import Counter
from typing import List, Tuple
from sklearn.cluster import AgglomerativeClustering

from DataProvider import DataProvider
from DinnerRouteList import DinnerRoute
from logger.Log import Log


class ClustererNewMealAssignments(Clusterer):

    def __init__(self, data_provider: DataProvider):
        """
        Given DataProvider instance, initializes the RecursiveClustererNewMealAssignments with following attributes:
        routes: List with route information (from DataProvider)
        dist_matrix: 2D numpy array with pairwise distances
        cluster_sizes: list of ints, indicating the original number of clusters and the value of each element indicates the size of the cluster
        """
        self.routes = data_provider.get_routes()
        self.dist_matrix = data_provider.get_distance_matrix()
        self.cluster_sizes = data_provider.get_cluster_sizes()
        self.cluster_templates = data_provider.get_cluster_template()
        self.cluster_templates = sorted(
            self.cluster_templates,
            key=lambda template: len(template)
        )
        self.data_provider = data_provider

    def __predict_draft(self):
        n_clusters = len(self.cluster_sizes)

        model = AgglomerativeClustering(
            metric='precomputed',
            linkage='complete',
            n_clusters=n_clusters,
        )
        labels = model.fit_predict(self.dist_matrix)
        for route, label in zip(self.routes, labels):
            route.clusterNumber = label

    def __get_route_clusters_sorted_by_cluster_size(self):
        cluster_labels_sorted: List[int] = sorted({route.clusterNumber for route in self.routes})
        routes_by_cluster_list: List[List[DinnerRoute]] = []
        for cluster_label in cluster_labels_sorted:
            routes_of_cluster = [route for route in self.routes if route.clusterNumber == cluster_label]
            routes_by_cluster_list.append(routes_of_cluster)
        return sorted(routes_by_cluster_list, key=lambda r: len(r))


    def __remove_excess_teams_from_cluster(self, routes_of_cluster: List[DinnerRoute], excess: int) -> list:
        """
        Given a list of routes belonging to the same cluster and the number of excess teams, 
        identifies the indices of the routes to be removed from the cluster based on their mean distance to other cluster members.
        Returns a list of indices of routes to be removed.
        """
        all_cluster_indices = set([route.originalIndex for route in routes_of_cluster])
        # Compute mean distance to other cluster members
        mean_dists = []
        for idx in all_cluster_indices:
            others = list(all_cluster_indices - {idx})
            if others:
                mean_dist = self.dist_matrix[idx, others].mean()
            else:
                mean_dist = 0
            mean_dists.append((mean_dist, idx))
        # Remove the ones with the largest mean distance
        mean_dists.sort(reverse=True)
        indices_to_remove = set()
        for _, idx in mean_dists[:excess]:
            indices_to_remove.add(idx)
        return list(indices_to_remove)

    def __balance_meals_in_cluster(self, routes_of_cluster: List[DinnerRoute], cluster_template: List[str]):
        meal_labels_current_cluster = [route.meal.label for route in routes_of_cluster]
        current_counts = Counter(meal_labels_current_cluster)
        required_counts = Counter(cluster_template)
        cluster_label = routes_of_cluster[0].clusterNumber

        Log.info(f"Current meal class counts: {current_counts} in cluster {cluster_label} with size {len(routes_of_cluster)}")
        Log.info(f"Required meal class counts: {required_counts} in cluster template with size {len(cluster_template)}")
        for meal_label, required_count in required_counts.items():
            current_count = current_counts.get(meal_label, 0)
            if current_count < required_count:
                # Need to add more of this meal class
                deficit = required_count - current_count
                Log.info(f"Need to add {deficit} of meal class {meal_label} to cluster {cluster_label}")

                for _ in range(deficit):
                    # Try to find a route from this cluster that has another meal classe which exceess the actual required total count of those meal classes for the current cluster
                    for other_meal_label, other_required_count in required_counts.items():
                        if other_meal_label == meal_label:
                            continue
                        other_current_count = current_counts.get(other_meal_label, 0)
                        if other_current_count > other_required_count:
                            # Found a meal class with excess
                            for route in routes_of_cluster:
                                if route.meal.label == other_meal_label:
                                    Log.info(f"Changing meal class of route {route} from {other_meal_label} to {meal_label}")
                                    route.meal = self.data_provider.get_meal_class_by_label(meal_label)
                                    current_counts[meal_label] += 1
                                    current_counts[other_meal_label] -= 1
                                    break
                            break

    def __get_non_removed_routes(self, routes: List[DinnerRoute]) -> List[DinnerRoute]:
        return [route for route in routes if route.clusterNumber != -1]

    def predict(self) -> Tuple[List[DinnerRoute], List[int]]:
        self.__predict_draft()

        route_clusters_sorted = self.__get_route_clusters_sorted_by_cluster_size()

        available_indices = set([])

        # Iterate over each cluster and remove excess teams in each cluster (note, both clusters and cluster_templates are sorted asc, this is important!).
        # Examples:
        # a) 2 Clusters with sizes of 5 and 16 teams. Cluster Template Sizes are [9, 12]
        #   ==> Cluster 1) has no excess (no action), Cluster 2) has excess of 4 teams, remove excess teams without considering meal classes
        # b) 3 Clusters with sizes of 7, 10 and 10 teams. Cluster Template Sizes are [9, 9, 9]
        #   ==> Cluster 1) has no excess (no action), Cluster 2) and 3) have both excess of 1 team, remove both excess teams without considering meal classes
        for route_cluster_idx, routes_of_cluster in enumerate(route_clusters_sorted):
            num_teams_in_cluster = len(routes_of_cluster)

            cluster_label = routes_of_cluster[0].clusterNumber
            Log.info(f"Cluster {cluster_label} has currently {num_teams_in_cluster} teams:")
            matching_cluster_template = self.cluster_templates[route_cluster_idx]
            expected_cluster_size = len(matching_cluster_template)
            # Remove excess teams (despite their meal class) if cluster size exceeds the expected size
            if num_teams_in_cluster > expected_cluster_size:
                excess = num_teams_in_cluster - expected_cluster_size
                Log.info(f"Cluster {cluster_label} has excess of {excess} teams, removing excess teams without considering meal classes")
                removed_indices = self.__remove_excess_teams_from_cluster(routes_of_cluster, excess)
                available_indices.update(removed_indices)
                Log.info(f"Removing indices {removed_indices} from cluster {cluster_label}")
                for route in routes_of_cluster:
                    if route.originalIndex in removed_indices:
                        route.clusterNumber = -1  # Mark as removed


        # Now add missing teams to each cluster which have less teams than expected based on the cluster template.
        # When adding teams, choose the ones that are closest to the cluster (based on distance matrix)
        # We ignore meal classes for now, we will re-assign them later in the final step
        for route_cluster_idx, route_cluster in enumerate(route_clusters_sorted):
            routes_of_cluster = self.__get_non_removed_routes(route_cluster)
            num_teams_in_cluster = len(routes_of_cluster)
            cluster_label = routes_of_cluster[0].clusterNumber
            matching_cluster_template = self.cluster_templates[route_cluster_idx]
            expected_cluster_size = len(matching_cluster_template)
            if num_teams_in_cluster < expected_cluster_size:
                missing = expected_cluster_size - num_teams_in_cluster
                Log.info(f"Cluster {cluster_label} has shortage of {missing} teams, adding missing teams without considering meal classes")
                # Get available indices sorted by mean distance to the cluster
                available_indices_sorted = []
                for idx in available_indices:
                    mean_dist_to_cluster = self.dist_matrix[idx, [route.originalIndex for route in routes_of_cluster]].mean()
                    available_indices_sorted.append((mean_dist_to_cluster, idx))
                available_indices_sorted.sort()
                # Add closest missing teams to the cluster
                indices_to_remove = []
                for _, idx in available_indices_sorted[:missing]:
                    Log.info(f"Adding index {idx} to cluster {cluster_label}")
                    indices_to_remove.append(idx)
                    for route in self.routes:
                        if route.originalIndex == idx:
                            route.clusterNumber = cluster_label
                            break
                for idx in indices_to_remove:
                    available_indices.remove(idx)                    

        # Assert we now have the correct number of teams in each cluster, if not, raise an error
        route_clusters_sorted = self.__get_route_clusters_sorted_by_cluster_size()
        for route_cluster_idx, routes_of_cluster in enumerate(route_clusters_sorted):
            routes_of_cluster = self.__get_non_removed_routes(routes_of_cluster)
            num_teams_in_cluster = len(routes_of_cluster)
            assert num_teams_in_cluster > 0, f"Cluster with index {route_cluster_idx} has no teams after excess removal and missing team addition, this should not happen"
            cluster_label = routes_of_cluster[0].clusterNumber
            matching_cluster_template = self.cluster_templates[route_cluster_idx]
            expected_cluster_size = len(matching_cluster_template)
            assert num_teams_in_cluster == expected_cluster_size, f"Cluster {cluster_label} has {num_teams_in_cluster} teams, but expected {expected_cluster_size} teams based on cluster template"

        # Now we have the correct number of teams in each cluster, but meal classes might be assigned in a way that does not match the required meal class counts in the cluster templates.
        for route_cluster_idx, routes_of_cluster in enumerate(route_clusters_sorted):
            matching_cluster_template = self.cluster_templates[route_cluster_idx]
            self.__balance_meals_in_cluster(routes_of_cluster, matching_cluster_template)

        final_routes = []
        final_cluster_labels = []
        for routes_of_cluster in route_clusters_sorted:
            final_routes.extend(routes_of_cluster)
            final_cluster_labels.extend([routes_of_cluster[0].clusterNumber for _ in routes_of_cluster])
        return final_routes, final_cluster_labels