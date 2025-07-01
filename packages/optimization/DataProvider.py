import pandas as pd
import numpy as np
import json

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