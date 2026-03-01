import numpy as np

from Clusterer import Clusterer
from collections import Counter
from typing import List, Set, Tuple, Dict
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
        self.final_route_clusters: Dict[int, List[DinnerRoute]] = {}

    def predict(self) -> Tuple[List[DinnerRoute], List[int]]:
        self.__predict_draft()

        all_cluster_labels = sorted({route.clusterNumber for route in self.routes})
        iterated_cluster_labels = set()

        # Iterate through all cluster_templates and enlarge the smallest clusters so that they match the respective cluster_templates
        # All enlarged clusters (and only these ones!) are then final.
        for cluster_template_idx, cluster_template in enumerate(self.cluster_templates):
            expected_cluster_size = len(cluster_template)
            Log.info(f"Cluster Template {cluster_template_idx} needs size of {expected_cluster_size} teams")

            # Get route cluster with greatest distance to other clusters and size below expected cluster size.
            # This is the cluster we will try to enlarge to match the expected cluster size of the current cluster template.
            routes_of_cluster = self.__get_cluster_with_greatest_distance_to_other_clusters_below_size(expected_cluster_size, iterated_cluster_labels)
            if len(routes_of_cluster) > 0:
                cluster_label = routes_of_cluster[0].clusterNumber
                num_teams_in_cluster = len(routes_of_cluster)
            else:
                 # Special case, our cluster label was merged into other smaller clusters and does not exist any longer
                routes_of_cluster = []
                num_teams_in_cluster = 0
                cluster_label = self.__get_first_lost_cluster_label(all_cluster_labels, iterated_cluster_labels)

            Log.info(f"Current iterated route cluster {cluster_label} has size of {num_teams_in_cluster} teams")

            iterated_cluster_labels.add(cluster_label)

            if num_teams_in_cluster < expected_cluster_size:
                needed_teams = expected_cluster_size - num_teams_in_cluster
                Log.info(f"Cluster {cluster_label} has shortage of {needed_teams} teams, adding missing teams without considering meal classes")
                closest_teams: List[DinnerRoute] = self.__calculate_closest_teams_from_other_clusters(needed_teams, cluster_label)
                for route in closest_teams:
                    Log.info(f"Adding team from cluster {route.clusterNumber} to cluster {cluster_label} to meet expected cluster size of {expected_cluster_size}")
                    route.clusterNumber = cluster_label
                self.final_route_clusters[cluster_label] = [route for route in self.routes if route.clusterNumber == cluster_label]
            elif num_teams_in_cluster == expected_cluster_size:
                Log.info(f"Cluster {cluster_label} already has the expected size of {expected_cluster_size} teams, adding it to final clusters")
                self.final_route_clusters[cluster_label] = routes_of_cluster

        # Now all not finalized clusters should have automatically proper size. We can now add all remaining clusters to the final clusters
        final_cluster_labels = self.final_route_clusters.keys()
        remaining_cluster_labels = [label for label in all_cluster_labels if label not in final_cluster_labels]
        for cluster_label in remaining_cluster_labels:
            Log.info(f"Adding remaining cluster {cluster_label} to final clusters")
            self.final_route_clusters[cluster_label] = [route for route in self.routes if route.clusterNumber == cluster_label]    

        # Assert all clusters are sized properly
        route_clusters_sorted_by_size = self.__get_route_clusters_sorted_by_cluster_size()
        for route_cluster_idx, routes_of_cluster in enumerate(route_clusters_sorted_by_size):
            num_teams_in_cluster = len(routes_of_cluster)
            cluster_label = routes_of_cluster[0].clusterNumber
            matching_cluster_template = self.cluster_templates[route_cluster_idx]
            expected_cluster_size = len(matching_cluster_template)
            assert num_teams_in_cluster == expected_cluster_size, f"Cluster {cluster_label} has {num_teams_in_cluster} teams, but expected {expected_cluster_size} teams based on cluster template after finalizing all clusters"

        # Final output
        final_routes = []
        final_cluster_labels = []
        for cluster_routes in self.final_route_clusters.values():
            matching_cluster_template = [cluster_template for cluster_template in self.cluster_templates if len(cluster_template) == len(cluster_routes)][0]
            self.__balance_meals_in_cluster(cluster_routes, matching_cluster_template)
            final_routes.extend(cluster_routes)
            final_cluster_labels.extend([cluster_routes[0].clusterNumber for _ in cluster_routes])
        return final_routes, final_cluster_labels

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


    def __get_cluster_with_greatest_distance_to_other_clusters_below_size(self, max_cluster_size: int, iterated_cluster_labels: Set[int]) -> List[DinnerRoute]:
        cluster_labels_sorted = sorted({route.clusterNumber for route in self.routes if route.clusterNumber not in iterated_cluster_labels})
        
        if len(cluster_labels_sorted) == 1:
            # only one candidate cluster, return it immediately
            return self.__filter_routes_by_label(cluster_labels_sorted[0])
        if len(cluster_labels_sorted) == 2:
            cluster_0 = self.__filter_routes_by_label(cluster_labels_sorted[0])
            cluster_1 = self.__filter_routes_by_label(cluster_labels_sorted[1])
            # If there are only two candidate clusters, we must skip distance calculation, due to we iterate cluster templates by size in outer function
            # and for our algorithm to work (never shrink too big clusters, only enlarge smaller clusters), we need to always pick the smaller cluster of the two candidate clusters:
            if len(cluster_0) < len(cluster_1):
                return cluster_0
            return cluster_1
        
        candidate_clusters: List[List[DinnerRoute]] = []
        for cluster_label in cluster_labels_sorted:
            routes_of_cluster = [route for route in self.routes if route.clusterNumber == cluster_label]
            if len(routes_of_cluster) <= max_cluster_size:
                candidate_clusters.append(routes_of_cluster)

        max_mean_distance = -1
        cluster_with_max_distance = None
        for candidate_cluster_routes in candidate_clusters:
            candidate_cluster_label = candidate_cluster_routes[0].clusterNumber
            other_routes = [route for route in self.routes if route.clusterNumber != candidate_cluster_label]
            other_indices = [route.originalIndex for route in other_routes]
            candidate_cluster_indices = [route.originalIndex for route in candidate_cluster_routes]

            mean_distance_to_other_clusters = self.dist_matrix[np.ix_(candidate_cluster_indices, other_indices)].mean()
            if mean_distance_to_other_clusters > max_mean_distance:
                max_mean_distance = mean_distance_to_other_clusters
                cluster_with_max_distance = candidate_cluster_routes

        if cluster_with_max_distance is None:
            return []
        return cluster_with_max_distance

    def __filter_routes_by_label(self, cluster_label: int) -> List[DinnerRoute]:
        return [route for route in self.routes if route.clusterNumber == cluster_label]

    def __calculate_closest_teams_from_other_clusters(self, num_needed_teams: int, target_cluster_label: int) -> List[DinnerRoute]:
        target_cluster_routes = [route for route in self.routes if route.clusterNumber == target_cluster_label]
        target_cluster_indices = [route.originalIndex for route in target_cluster_routes]

        cluster_labels_already_finalized = self.final_route_clusters.keys()
        other_cluster_routes = [route for route in self.routes if route.clusterNumber != target_cluster_label]
        other_cluster_routes = [r for r in other_cluster_routes if r.clusterNumber not in cluster_labels_already_finalized]
        other_cluster_indices = [route.originalIndex for route in other_cluster_routes]

        mean_distances = []
        for idx in other_cluster_indices:
            mean_distance = self.dist_matrix[idx, target_cluster_indices].mean()
            mean_distances.append((mean_distance, idx))

        mean_distances.sort()
        closest_teams = []
        for _, idx in mean_distances[:num_needed_teams]:
            for route in other_cluster_routes:
                if route.originalIndex == idx:
                    closest_teams.append(route)
                    break
        return closest_teams

    # def __get_remaining_route_clusters_sorted_by_cluster_size(self, iterated_cluster_labels: Set[int]) -> List[List[DinnerRoute]]:
    #     # cluster_labels_already_finalized = self.final_route_clusters.keys()
    #     cluster_labels_sorted: List[int] = sorted({route.clusterNumber for route in self.routes if route.clusterNumber not in iterated_cluster_labels})
    #     routes_by_cluster_list: List[List[DinnerRoute]] = []
    #     for cluster_label in cluster_labels_sorted:
    #         routes_of_cluster = [route for route in self.routes if route.clusterNumber == cluster_label]
    #         routes_by_cluster_list.append(routes_of_cluster)
    #     return sorted(routes_by_cluster_list, key=lambda r: len(r))

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

    def __get_first_lost_cluster_label(self, all_cluster_labels: List[int], iterated_cluster_labels: Set[int]) -> int:
        for cluster_label in all_cluster_labels:
            if cluster_label not in iterated_cluster_labels:
                return cluster_label
        raise Exception("All cluster labels have already been iterated, but at least one more cluster label is needed")

    def __get_route_clusters_sorted_by_cluster_size(self):
        routes = [route for cluster_routes in self.final_route_clusters.values() for route in cluster_routes]
        cluster_labels_sorted: List[int] = sorted({route.clusterNumber for route in routes})
        routes_by_cluster_list: List[List[DinnerRoute]] = []
        for cluster_label in cluster_labels_sorted:
            routes_of_cluster = [route for route in routes if route.clusterNumber == cluster_label]
            routes_by_cluster_list.append(routes_of_cluster)
        return sorted(routes_by_cluster_list, key=lambda r: len(r))
