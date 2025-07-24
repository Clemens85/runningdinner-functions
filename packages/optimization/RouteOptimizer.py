from Clusterer import Clusterer
from DataProvider import DataProvider
from DinnerRouteList import DinnerRoute, DinnerRouteList
from RouteBuilder import RouteBuilder, calculate_distance_sum
from loaders.DataLoader import  DataLoader
from logger.Log import Log
import itertools
from response import ResponseHandler
from typing import List

class RouteOptimizer:
    def __init__(self, data_loader: DataLoader, response_handler: ResponseHandler):
        self.data_loader = data_loader
        self.response_handler = response_handler

    def optimize(self):
        data = DataProvider(self.data_loader)
        original_routes = data.get_routes()
        original_distance_sum = calculate_distance_sum(original_routes, data.get_distance_matrix())
        Log.info(f"Original distance sum: {original_distance_sum:2f} m")

        clusterer = Clusterer(data)
        optimized_route_clusters, labels = clusterer.predict()
        
        Log.info(labels)

        cluster_labels = sorted(set(labels))

        optimized_routes: List[List[DinnerRoute]] = []
        route_builder = RouteBuilder(data, optimized_route_clusters)
        for cluster_label in cluster_labels:
            final_route_cluster, _ = route_builder.build_route_for_cluster_label(cluster_label)
            optimized_routes.append(final_route_cluster)

        result: List[DinnerRoute] = list(itertools.chain.from_iterable(optimized_routes))
        optimized_distance_sum = calculate_distance_sum(result, data.get_distance_matrix())
        Log.info(f"Optimized distance sum: {optimized_distance_sum:2f} m")

        dinner_route_list: DinnerRouteList = DinnerRouteList(
            adminId = data.get_admin_id(),
            optimizationId = data.get_optimization_id(),
            dinnerRoutes = result, 
            distanceMatrix = [], 
            clusterSizes = {},
            meals = []
        )
        result_json = dinner_route_list.model_dump_json(indent=2)
        self.response_handler.send(result_json)

        return result, optimized_distance_sum