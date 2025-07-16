import pandas as pd
import numpy as np

from MatrixTemplates import get_matrix_for_cluster_size, get_matrixes_for_cluster_size

class RouteBuilder:
    def __init__(self, routes: pd.DataFrame, dist_matrix: list[list[float]]):
        self.routes = routes.copy() # Ensure we don't modify the original DataFrame
        self.dist_matrix = np.array(dist_matrix)
        self.meal_classes = self.routes["mealClass"].unique()  # e.g. ['Vorspeise', 'Hauptspeise', 'Nachspeise']

    def build_route_for_cluster_label(self, cluster_label: int):
        """
        Builds a route for a specific cluster label.
        """
        if 'clusterNumber' not in self.routes.columns:
            raise ValueError("The routes DataFrame must contain a 'clusterNumber' column.")
        
        
        cluster_routes = self.routes[self.routes['clusterNumber'] == cluster_label].copy()
        if cluster_routes.empty:
            raise ValueError(f"No routes found for cluster label {cluster_label}.")
        
        # Get size of cluster_routes dataframe
        cluster_size = cluster_routes.shape[0]
        matrix = self.__get_random_matrix_for_cluster_size(cluster_size)

        meal_class_groups = cluster_routes.groupby('mealClass')

        for i, meal_rows in enumerate(matrix):
            for j, meal in enumerate(meal_rows):
                hoster_number = meal[0]
                

    def __get_random_matrix_for_cluster_size(self, cluster_size: int) -> list[list[list[int]]]:
        """ Returns a random matrix for the given cluster size.
        """
        matrixes_list = get_matrixes_for_cluster_size(cluster_size)
        if not matrixes_list:
            raise ValueError(f"No matrix defined for cluster size {cluster_size}.")
        return np.random.choice(matrixes_list)
    
