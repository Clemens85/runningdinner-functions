from collections import Counter

from Clusterer import Clusterer
from DataProvider import DataProvider

WORKSPACE_BASE_DIR = 'test-data'


def load_sample_data(filename: str) -> DataProvider:
  data = DataProvider(f'{WORKSPACE_BASE_DIR}/{filename}')
  return data


def test_predict_3_team_clusters():
    data = load_sample_data("27_teams_3ce786ba.json")

    original_routes = data.get_routes()
    # TODO
    expected_original_cluster_labels = original_routes['clusterNumber'].values

    assert data.get_cluster_template()[0] == ['Hauptspeise', 'Hauptspeise', 'Hauptspeise', 'Nachspeise', 'Nachspeise', 'Nachspeise', 'Vorspeise', 'Vorspeise', 'Vorspeise']

    clusterer = Clusterer(data)
    final_routes, final_labels = clusterer.predict()
    assert len(final_routes) == 27
    assert len(final_labels) == 27
    assert set(final_labels) == {0, 1, 2}

    # Ensure that the original cluster labels are preserved
    original_cluster_labels = [route.clusterNumber for route in data.get_routes()]
    assert all([a == b] for a, b in zip(original_cluster_labels, expected_original_cluster_labels))

    for cluster_label in range (3):
        print (f"Asserting cluster {cluster_label} has 9 items")
        routes_of_cluster = [route for route in final_routes if route.clusterNumber == cluster_label]
        assert len(routes_of_cluster) == 9
        for meal_class in (["Vorspeise", "Hauptspeise", "Nachspeise"]):
          print (f"Asserting cluster {cluster_label} has 3 occurrences of {meal_class}")
          sum_meal = len([route for route in routes_of_cluster if route.mealClass == meal_class])
          assert sum_meal == 3


def test_predict_5_team_clusters():
    data = load_sample_data("45_teams_b17d628f.json")

    original_routes = data.get_routes()

    clusterer = ClustererAgg(original_routes, data.get_distance_matrix(), data.get_cluster_sizes())
    num_expected_clusters = len(data.get_cluster_sizes())
    assert num_expected_clusters == 5

    _, labels = clusterer.predict(n_clusters = num_expected_clusters)
    assert len(labels) == 45
    assert set(labels) == {0, 1, 2, 3, 4}

    final_routes, final_labels = clusterer.predict_exact(data.get_cluster_template())
    assert len(final_labels) == 45
    assert set(final_labels) == {0, 1, 2, 3, 4}

    for cluster_label in range (5):
        print (f"Asserting cluster {cluster_label} has 9 items")
        meal_classes_of_cluster = final_routes[final_routes["clusterNumber"] == cluster_label]["mealClass"].values
        assert len(meal_classes_of_cluster) == 9
        for _, meal_class in enumerate(["Vorspeise", "Hauptspeise", "Nachspeise"]):
          print (f"Asserting cluster {cluster_label} has 3 occurrences of {meal_class}")
          sum_meal = len(final_routes[(final_routes["clusterNumber"] == cluster_label) & (final_routes["mealClass"] == meal_class)]["mealClass"].values)
          assert sum_meal == 3


def test_predict_2_team_clusters_different_sizes():
    data = load_sample_data("21_teams_274fc6d7.json")

    original_routes = data.get_routes()

    clusterer = ClustererAgg(original_routes, data.get_distance_matrix(), data.get_cluster_sizes())
    num_expected_clusters = len(data.get_cluster_sizes())
    assert num_expected_clusters == 2

    _, labels = clusterer.predict(n_clusters = num_expected_clusters)
    assert len(labels) == 21
    assert set(labels) == {0, 1}

    final_routes, final_labels = clusterer.predict_exact(data.get_cluster_template())
    assert len(final_labels) == 21
    unique_cluster_labels = set(final_labels)
    assert unique_cluster_labels == {0,1}

    # Create new list from unique_cluster_labels so that the order of list is desc by occurence of cluster label
    counter = Counter(final_labels)
    unique_cluster_labels = [item for item, count in counter.most_common()][::-1] # [::-1] reverts the list, so that it's asc

    cluster_9 = unique_cluster_labels[0]
    meal_classes_of_cluster = final_routes[final_routes["clusterNumber"] == cluster_9]["mealClass"].values
    assert len(meal_classes_of_cluster) == 9
    for _, meal_class in enumerate(["Vorspeise", "Hauptspeise", "Nachspeise"]):
        print(f"Asserting cluster {cluster_9} has 3 occurrences of {meal_class}")
        sum_meal = len(final_routes[(final_routes["clusterNumber"] == cluster_9) & (final_routes["mealClass"] == meal_class)]["mealClass"].values)
        assert sum_meal == 3

    cluster_12 = unique_cluster_labels[1]
    meal_classes_of_cluster = final_routes[final_routes["clusterNumber"] == cluster_12]["mealClass"].values
    assert len(meal_classes_of_cluster) == 12
    for _, meal_class in enumerate(["Vorspeise", "Hauptspeise", "Nachspeise"]):
        print(f"Asserting cluster {cluster_12} has 4 occurrences of {meal_class}")
        sum_meal = len(final_routes[(final_routes["clusterNumber"] == cluster_12) & (final_routes["mealClass"] == meal_class)]["mealClass"].values)
        assert sum_meal == 4