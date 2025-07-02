#from itertools import chain
import pandas as pd
import numpy as np
import json
import itertools
# from itertools import chain_from_iterable

class DataProvider:
    def __init__(self, file_path):
        self.__load(file_path)
        
    def __load(self, file_path):
        with open(file_path) as f:
            data = json.load(f)

        self.routes = pd.DataFrame(data['dinnerRoutes'])
        self.dist_matrix = np.array(data['distanceMatrix'])
        self.cluster_sizes = [len(v) for v in data["clusterSizes"].values()]
        self.routes["mealClass"] = [route["meal"]["label"] for route in data["dinnerRoutes"]]
        
    def get_routes(self):
        return self.routes

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
        mealClasses = self.routes["mealClass"].unique() # Vorspeise, Hauptspeise, Nachspeise
        for cluster_size in self.get_cluster_sizes():
            # cluster_size is e.g. 9
            meal_class_amounts = cluster_size / mealClasses.size
            meal_classes_of_cluster = []
            for mealClass in mealClasses:
                meal_classes_of_cluster.append([mealClass for _ in range(int(meal_class_amounts))])
            result.append(list(itertools.chain.from_iterable(meal_classes_of_cluster)))
        return result