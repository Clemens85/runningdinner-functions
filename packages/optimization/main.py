from DataProvider import DataProvider
from Visualizer import Visualizer
from Clusterer import Clusterer

WORKSPACE_BASE_DIR = "/home/clemens/Projects/ml/bin/workspace/geocoding"

def main():
  data = DataProvider(f"{WORKSPACE_BASE_DIR}/data/27_teams_3ce786ba.json")
  routes = data.get_routes()
  dist_matrix = data.get_distance_matrix()

  cluster_sizes = data.get_cluster_sizes()
  print(f"Cluster sizes: {cluster_sizes}")

  # clusterer = Clusterer(routes, dist_matrix, n_clusters=3)
  clusterer = Clusterer(routes, dist_matrix, algorithm="balanced", cluster_sizes=cluster_sizes)
  optimizedRoutes, labels = clusterer.cluster()
  print(labels)

  # vis = Visualizer(routes, dist_matrix)
  # vis.plot_geocodes()

if __name__ == "__main__":
    main()