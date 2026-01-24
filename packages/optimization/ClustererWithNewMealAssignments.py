from Clusterer import Clusterer
from collections import Counter
from typing import Dict, List, Tuple
import numpy as np
from sklearn.cluster import AgglomerativeClustering

from DataProvider import DataProvider
from DinnerRouteList import DinnerRoute
from logger.Log import Log


class ClustererWithNewMealAssignments(Clusterer):

    def __init__(self, data_provider: DataProvider):
        """
        Given DataProvider instance, initializes the ClustererWithNewMealAssignments with following attributes:
        routes: List with route information (from DataProvider)
        dist_matrix: 2D numpy array with pairwise distances
        cluster_sizes: list of ints, indicating the original number of clusters and the value of each element indicates the size of the cluster
        """
        self.routes = data_provider.get_routes()
        self.dist_matrix = data_provider.get_distance_matrix()
        self.cluster_sizes = data_provider.get_cluster_sizes()
        self.cluster_templates = data_provider.get_cluster_template()
        self.cluster_templates= sorted(
            self.cluster_templates,
            key=lambda template: len(template)
        )
        self.final_route_clusters: Dict[int, List[DinnerRoute]] = {}
        self.data_provider = data_provider

    def predict(self) -> Tuple[List[DinnerRoute], List[int]]:
        n_clusters = len(self.cluster_sizes)
        for n_cluster in range(n_clusters, 0, -1):
            Log.info(f"Building cluster number {n_cluster} out of total of {n_clusters}...")
            # reset route cluster numbers to -1 for remaining routes
            for route in self.routes:
                route.clusterNumber = -1
            self.__predict_cluster(n_cluster)

        # decrement cluster numbers to start from 0
        for route in self.final_route_clusters.values():
            for r in route:
                r.clusterNumber -= 1
        # prepare final output
        final_routes = []
        final_cluster_labels = []
        for cluster_routes in self.final_route_clusters.values():
            final_routes.extend(cluster_routes)
            final_cluster_labels.extend([cluster_routes[0].clusterNumber for _ in cluster_routes])
        return final_routes, final_cluster_labels

    def __predict_cluster(self, n_clusters: int):

        # When n_clusters == 1, assign all remaining routes to the last cluster template
        if n_clusters == 1:
            route_cluster = self.routes
            for route in route_cluster:
                route.clusterNumber = n_clusters
            cluster_template = self.cluster_templates[-1]
        else:    
            model = AgglomerativeClustering(
                metric='precomputed',
                linkage='complete',
                n_clusters=n_clusters,
            )
            labels = model.fit_predict(self.dist_matrix)
            for route, label in zip(self.routes, labels):
                route.clusterNumber = label

            cluster_labels_sorted: List[int] = sorted({route.clusterNumber for route in self.routes})
            routes_by_cluster_list: List[List[DinnerRoute]] = []
            for cluster_label in cluster_labels_sorted:
                routes_of_cluster = [route for route in self.routes if route.clusterNumber == cluster_label]
                routes_by_cluster_list.append(routes_of_cluster)
            self.routes_by_cluster_list = sorted(routes_by_cluster_list, key=lambda r: len(r))

            cluster_template, route_cluster = self.__get_fitting_cluster_template()

        # For each meal in the cluster template, take one dinner route team from the route_cluster
        # If no dinner route team with the required meal class is available, take any dinner route team from another cluster and change its meal class
        # Repeat until all meal classes in the cluster template are assigned
        meal_labels_current_cluster = [route.meal.label for route in route_cluster]
        current_counts = Counter(meal_labels_current_cluster)
        required_counts = Counter(cluster_template)
        Log.info(f"Current meal class counts: {current_counts} in cluster {route_cluster[0].clusterNumber} with size {len(route_cluster)}")
        Log.info(f"Required meal class counts: {required_counts} in cluster template with size {len(cluster_template)}")
        for meal_label, required_count in required_counts.items():
            current_count = current_counts.get(meal_label, 0)
            if current_count < required_count:
                # Need to add more of this meal class
                deficit = required_count - current_count
                Log.info(f"Need to add {deficit} of meal class {meal_label} to cluster {route_cluster[0].clusterNumber}")
                for _ in range(deficit):
                    # Try to find a route from this cluster that has another meal classe which exceess the actual required total count of those meal classes for the current cluster
                    for other_meal_label, other_required_count in required_counts.items():
                        if other_meal_label == meal_label:
                            continue
                        other_current_count = current_counts.get(other_meal_label, 0)
                        if other_current_count > other_required_count:
                            # Found a meal class with excess
                            for route in route_cluster:
                                if route.meal.label == other_meal_label:
                                    Log.info(f"Changing meal class of route {route} from {other_meal_label} to {meal_label}")
                                    route.meal = self.data_provider.get_meal_class_by_label(meal_label)
                                    current_counts[meal_label] += 1
                                    current_counts[other_meal_label] -= 1
                                    break
                            break
        
        if len(route_cluster) > len(cluster_template):
            # remove excess routes from the cluster (those which have more than required meal classes)
            for meal_label, required_count in required_counts.items():
                current_count = current_counts.get(meal_label, 0)
                if current_count > required_count:
                    # Need to remove some of this meal class
                    excess = current_count - required_count
                    Log.info(f"Need to remove {excess} of meal class {meal_label}")
                    route_cluster_subset = [route for route in route_cluster if route.meal.label == meal_label]
                    # Further optimization possibility: remove routes which are furthest away from the cluster center
                    routes_to_remove = route_cluster_subset[:excess]
                    for route in routes_to_remove:
                        route_cluster.remove(route)
                    current_counts[meal_label] -= excess
        
        if current_counts != required_counts:
            Log.error(f"After meal assignment, current counts do not match required counts!")
            Log.error(f"Current meal class counts: {current_counts}")
            Log.error(f"Required meal class counts: {required_counts}") 
            raise ValueError("Meal class assignment failed to match required counts.")

        # Assign cluster number to all routes in the route_cluster
        for route in route_cluster:
            route.clusterNumber = n_clusters
        self.final_route_clusters[n_clusters] = route_cluster

        # Remove assigned routes from self.routes and adapt distance matrix by removing those assigned routes
        # 1) Identify indices to keep BEFORE removing routes
        team_ids_of_cluster = {route.teamId for route in route_cluster}
        indices_to_keep = [i for i, route in enumerate(self.routes) if route.teamId not in team_ids_of_cluster]
        # 2) Now remove assigned routes from self.routes
        self.routes = [route for route in self.routes if route.teamId not in team_ids_of_cluster]
        # 3) Adapt distance matrix using the indices we identified earlier
        self.dist_matrix = self.dist_matrix[np.ix_(indices_to_keep, indices_to_keep)]


    def __get_fitting_cluster_template(self) -> Tuple[List[str], List[DinnerRoute]]:
        """
        Find a cluster template alongside with the matched route cluster, that fits one of the predicted clusters.
        A cluster which is smaller as the smallest template cannot be matched.
        Try to use the smallest possible cluster template that fits.
        """
        best_matched_route_cluster = None
        matched_cluster_template_idx = None
        for idx, cluster_template in enumerate(self.cluster_templates):
            for routes_of_cluster in self.routes_by_cluster_list:
                if len(routes_of_cluster) >= len(cluster_template):
                    if best_matched_route_cluster is None or len(routes_of_cluster) < len(best_matched_route_cluster):
                        best_matched_route_cluster = routes_of_cluster
                        matched_cluster_template_idx = idx
            break # Either found the best fitting template or none fits (due to sorting by size we can stop here)

        if matched_cluster_template_idx is None:
            raise ValueError("No fitting cluster template found for remaining routes")
        
        matched_cluster_template = self.cluster_templates.pop(matched_cluster_template_idx)
        return matched_cluster_template, best_matched_route_cluster
