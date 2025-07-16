#from itertools import chain
from copy import deepcopy
from types import SimpleNamespace
import pandas as pd
import numpy as np
import json
import itertools

from DinnerRouteList import DinnerRouteList
# from itertools import chain_from_iterable

class DataProvider:
    def __init__(self, file_path):
        self.__load(file_path)
        
    def __load(self, file_path):
        # with open(file_path) as f:
        #     data_raw = json.load(f)

        with open(file_path) as f:
            data: DinnerRouteList = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

        # self.routes_obj: DinnerRouteList = json.loads(data['dinnerRoutes'], object_hook=lambda d: SimpleNamespace(**d))
        self.routes = data.dinnerRoutes
        self.dist_matrix = np.array(data.distanceMatrix)
        cluster_sizes_dict = vars(data.clusterSizes) # Converts SimpleNamespace to dict
        self.cluster_sizes = [len(v) for v in cluster_sizes_dict.values()]
        
        for index, route in enumerate(self.routes):
            route.originalIndex = index
            route.mealClass = route.meal.label

        # self.routes = pd.DataFrame(data_raw["dinnerRoutes"])
        # self.routes["mealClass"] = [route["meal"]["label"] for route in data_raw["dinnerRoutes"]]
        # self.routes["originalIndex"] = self.routes.index
   
    def get_routes(self):
        return deepcopy(self.routes)

    def get_distance_matrix(self):
        return self.dist_matrix
    
    def get_cluster_sizes(self):
        return self.cluster_sizes
    
    def get_distance_percentiles(self):
        dists = self.dist_matrix[np.triu_indices_from(self.dist_matrix, k=1)]
        dists = dists[dists > 0]
        percentiles = {p: np.percentile(dists, p) for p in [50, 70, 75, 80, 90, 95, 99]}
        return percentiles
    
    def get_cluster_template(self):
        """ Returns a list of lists, where each inner list contains meal classes for a cluster.
        For example, if there are 3 meal classes (Vorspeise, Hauptspeise, Nachspeise) and the cluster size is 9,
        it will return:
        [
            ['Vorspeise', 'Vorspeise', 'Vorspeise', 'Hauptspeise', 'Hauptspeise', 'Hauptspeise', 'Nachspeise', 'Nachspeise', 'Nachspeise']
        ]
        """
        result = []
        
        unique_meal_classes = sorted({route.mealClass for route in self.routes}) # Vorspeise, Hauptspeise, Nachspeise

        for cluster_size in self.get_cluster_sizes():
            # cluster_size is e.g. 9
            meal_class_amounts = cluster_size / len(unique_meal_classes)
            meal_classes_of_cluster = []
            for meal_class in unique_meal_classes:
                meal_classes_of_cluster.append([meal_class for _ in range(int(meal_class_amounts))])
            result.append(list(itertools.chain.from_iterable(meal_classes_of_cluster)))
        return result