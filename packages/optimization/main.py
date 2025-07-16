from Clusterer import Clusterer
from DataProvider import DataProvider

WORKSPACE_BASE_DIR = "/home/clemens/Projects/runningdinner-functions/packages/optimization/test-data"

def main():
  data = DataProvider(f"{WORKSPACE_BASE_DIR}/27_teams_3ce786ba.json")
  cluster_sizes = data.get_cluster_sizes()
  print(f"Cluster sizes: {cluster_sizes}")

  clusterer = Clusterer(data)
  optimized_routes, labels = clusterer.predict()
  print(labels)
  clusterer.print_max_distances_per_cluster(optimized_routes)


if __name__ == "__main__":
    main()