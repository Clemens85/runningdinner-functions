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

    def get_routes(self):
        return self.routes

    def get_distance_matrix(self):
        return self.dist_matrix
    
    def get_cluster_sizes(self):
        return self.cluster_sizes