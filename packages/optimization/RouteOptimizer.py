import json

from ClustererFactory import get_clusterer_instance
from DataProvider import DataProvider
from DinnerRouteList import DinnerRoute, DinnerRouteList
from RouteBuilder import RouteBuilder, calculate_distance_sum
from loaders.DataLoader import  DataLoader
from logger.Log import Log
import itertools
from response.ResponseHandler import ResponseHandler
from response.EventMapper import EventMapper
from typing import List

class RouteOptimizer:
    def __init__(self, data_loader: DataLoader, response_handler: ResponseHandler):
        self.data_loader = data_loader
        self.data = DataProvider(data_loader)
        self.response_handler = response_handler
        self.event_mapper = EventMapper(admin_id=self.data.get_admin_id(), optimization_id=self.data.get_optimization_id())

    def optimize(self):
        try:
            return self._perform_optimization()
        except Exception as e:
            self._process_error(e)
            raise e

    def _perform_optimization(self):
        original_routes = self.data.get_routes()
        original_distance_sum = calculate_distance_sum(original_routes, self.data.get_distance_matrix())
        Log.info(f"Original distance sum: {original_distance_sum:2f} m")

        clusterer = get_clusterer_instance(self.data)
        optimized_route_clusters, labels = clusterer.predict()
        
        Log.info(labels)

        cluster_labels = sorted(set(labels))

        optimized_routes: List[List[DinnerRoute]] = []
        route_builder = RouteBuilder(self.data, optimized_route_clusters)
        for cluster_label in cluster_labels:
            final_route_cluster, _ = route_builder.build_route_for_cluster_label(cluster_label)
            optimized_routes.append(final_route_cluster)

        result: List[DinnerRoute] = list(itertools.chain.from_iterable(optimized_routes))
        optimized_distance_sum = calculate_distance_sum(result, self.data.get_distance_matrix())
        Log.info(f"Optimized distance sum: {optimized_distance_sum:2f} m")

        admin_id = self.data.get_admin_id()
        optimization_id = self.data.get_optimization_id()

        dinner_route_list: DinnerRouteList = DinnerRouteList(
            adminId = admin_id,
            optimizationId = optimization_id,
            dinnerRoutes = result, 
            distanceMatrix = [], 
            clusterSizes = {},
            meals = [],
            optimizationSettings=self.data.get_optimization_settings()
        )
        result_json = dinner_route_list.model_dump_json(indent=2)
        
        self.response_handler.send(result_json, self.event_mapper.new_optimization_finished_event())

        return result, optimized_distance_sum
    
    def _process_error(self, error: Exception):
        error_message = str(error)
        finished_event = self.event_mapper.new_optimization_error_event(error_message)
        
        error_json_wrapper = {
            "errorMessage": error_message,
        }
        error_json_str = json.dumps(error_json_wrapper)

        self.response_handler.send(error_json_str, finished_event)