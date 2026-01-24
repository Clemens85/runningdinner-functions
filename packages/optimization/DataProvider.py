from copy import deepcopy
from typing import List
import numpy as np
import json
import itertools

from DinnerRouteList import DinnerRouteList
from loaders.DataLoader import DataLoader

class DataProvider:
    def __init__(self, data_loader: DataLoader):
        self.__load(data_loader)
        
    def __load(self, data_loader: DataLoader):
        json_string = data_loader.load_json_string()
        data_tmp = json.loads(json_string)
        data = DinnerRouteList(**data_tmp)  # Convert dict to DinnerRouteList instance

        self.routes = data.dinnerRoutes
        self.dist_matrix = np.array(data.distanceMatrix)
        self.cluster_sizes = [len(v) for v in data.clusterSizes.values()]
        self.meal_classes = data.meals

        self.admin_id = data.adminId
        self.optimization_id = data.optimizationId

        self.optimization_settings = data.optimizationSettings
        
        for index, route in enumerate(self.routes):
            route.originalIndex = index
            route.mealClass = route.meal.label

    def get_routes(self):
        # return copy of routes to avoid unintended modifications
        return deepcopy(self.routes)

    def get_distance_matrix(self):
        # return copy of distance matrix to avoid unintended modifications
        return deepcopy(self.dist_matrix)
    
    def get_cluster_sizes(self):
        return self.cluster_sizes
    
    def get_distance_percentiles(self):
        dists = self.dist_matrix[np.triu_indices_from(self.dist_matrix, k=1)]
        dists = dists[dists > 0]
        percentiles = {p: np.percentile(dists, p) for p in [50, 70, 75, 80, 90, 95, 99]}
        return percentiles
    
    def get_cluster_template(self) -> List[List[str]]:
        """ Returns a list of lists, where each inner list contains meal classes for a cluster.
        For example, if there are 3 meal classes (Vorspeise, Hauptspeise, Nachspeise) and the cluster size is 9,
        it will return:
        [
            ['Vorspeise', 'Vorspeise', 'Vorspeise', 'Hauptspeise', 'Hauptspeise', 'Hauptspeise', 'Nachspeise', 'Nachspeise', 'Nachspeise']
        ]
        """
        result = []
        
        unique_meal_classes = self.get_unique_meal_classes_ordered() # Vorspeise, Hauptspeise, Nachspeise

        for cluster_size in self.get_cluster_sizes():
            # cluster_size is e.g. 9
            meal_class_amounts = cluster_size / len(unique_meal_classes)
            meal_classes_of_cluster = []
            for meal_class in unique_meal_classes:
                meal_classes_of_cluster.append([meal_class for _ in range(int(meal_class_amounts))])
            result.append(list(itertools.chain.from_iterable(meal_classes_of_cluster)))
        return result
    
    def get_unique_meal_classes_ordered(self):
        """ Returns a list of unique meal classes from the routes.
        """
        return [meal_class.label for meal_class in self.meal_classes]
    
    def get_admin_id(self):
        return self.admin_id
    
    def get_optimization_id(self):
        return self.optimization_id

    def get_optimization_settings(self):
        return self.optimization_settings