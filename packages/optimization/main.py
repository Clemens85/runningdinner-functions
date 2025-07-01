from DataProvider import DataProvider
from Visualizer import Visualizer
from ClustererAgg import ClustererAgg

WORKSPACE_BASE_DIR = "/home/clemens/Projects/runningdinner-functions/packages/optimization/test-data"

def main():
  data = DataProvider(f"{WORKSPACE_BASE_DIR}/27_teams_3ce786ba.json")
  routes = data.get_routes()
  dist_matrix = data.get_distance_matrix()
  cluster_sizes = data.get_cluster_sizes()
  print(f"Cluster sizes: {cluster_sizes}")

  clusterer = ClustererAgg(routes, dist_matrix, cluster_sizes=cluster_sizes)
  optimizedRoutes, labels = clusterer.predict(n_clusters=len(cluster_sizes) - 1)
  print(labels)
  clusterer.print_max_distances_per_cluster(optimizedRoutes)


if __name__ == "__main__":
    main()