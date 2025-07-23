from collections import Counter

from Clusterer import Clusterer
from DataProvider import DataProvider
from RouteBuilder import calculate_distance_sum
from RouteBuilder import RouteBuilder

WORKSPACE_BASE_DIR = 'test-data'

def load_sample_data(filename: str) -> DataProvider:
  data = DataProvider(f'{WORKSPACE_BASE_DIR}/{filename}')
  return data

def _get_routes_of_cluster_with_expected_size(routes, cluster_label, expected_size):
    print(f"Asserting cluster {cluster_label} has {expected_size} items")
    result = [route for route in routes if route.clusterNumber == cluster_label]
    assert len(result) == expected_size
    return result

def _get_routes_of_cluster_with_meal(routes, cluster_label, meal_class):
    result = [route for route in routes if route.clusterNumber == cluster_label]
    result = [route for route in result if route.mealClass == meal_class]
    return result

def test_predict_3_team_clusters():
    data = load_sample_data("27_teams_017662e4.json")

    assert data.get_cluster_template()[0] == ['Vorspeise', 'Vorspeise', 'Vorspeise', 'Hauptspeise', 'Hauptspeise', 'Hauptspeise', 'Nachspeise', 'Nachspeise', 'Nachspeise']

    clusterer = Clusterer(data)
    final_routes, final_labels = clusterer.predict()
    assert len(final_routes) == 27
    assert len(final_labels) == 27
    assert set(final_labels) == {0, 1, 2}

    for cluster_label in range (3):
        routes_of_cluster = _get_routes_of_cluster_with_expected_size(final_routes, cluster_label, 9)
        for meal_class in (["Vorspeise", "Hauptspeise", "Nachspeise"]):
          print (f"Asserting cluster {cluster_label} has 3 occurrences of {meal_class}")
          sum_meal = len([route for route in routes_of_cluster if route.mealClass == meal_class])
          assert sum_meal == 3

def test_predict_5_team_clusters():
    data = load_sample_data("45_teams_b17d628f.json")

    clusterer = Clusterer(data)
    num_expected_clusters = len(data.get_cluster_sizes())
    assert num_expected_clusters == 5

    final_routes, final_labels = clusterer.predict()
    assert len(final_labels) == 45
    assert set(final_labels) == {0, 1, 2, 3, 4}

    for cluster_label in range (5):
        routes_of_cluster = _get_routes_of_cluster_with_expected_size(final_routes, cluster_label, 9)
        for meal_class in (["Vorspeise", "Hauptspeise", "Nachspeise"]):
          print (f"Asserting cluster {cluster_label} has 3 occurrences of {meal_class}")
          sum_meal = len([route for route in routes_of_cluster if route.mealClass == meal_class])
          assert sum_meal == 3


def test_predict_2_team_clusters_different_sizes():
    data = load_sample_data("21_teams_274fc6d7.json")

    clusterer = Clusterer(data)
    num_expected_clusters = len(data.get_cluster_sizes())
    assert num_expected_clusters == 2

    final_routes, final_labels = clusterer.predict()
    assert len(final_labels) == 21
    unique_cluster_labels = set(final_labels)
    assert unique_cluster_labels == {0,1}

    # Create new list from unique_cluster_labels so that the order of list is desc by occurence of cluster label
    counter = Counter(final_labels)
    unique_cluster_labels = [item for item, count in counter.most_common()][::-1] # [::-1] reverts the list, so that it's asc

    cluster_9 = unique_cluster_labels[0]
    _get_routes_of_cluster_with_expected_size(final_routes, cluster_9, 9)
    for _, meal_class in enumerate(["Vorspeise", "Hauptspeise", "Nachspeise"]):
        print(f"Asserting cluster {cluster_9} has 3 occurrences of {meal_class}")
        route_hosts_with_meal_class = _get_routes_of_cluster_with_meal(final_routes, cluster_9, meal_class)
        sum_meal = len(route_hosts_with_meal_class)
        assert sum_meal == 3

    cluster_12 = unique_cluster_labels[1]
    _get_routes_of_cluster_with_expected_size(final_routes, cluster_12, 12)
    for _, meal_class in enumerate(["Vorspeise", "Hauptspeise", "Nachspeise"]):
        print(f"Asserting cluster {cluster_12} has 4 occurrences of {meal_class}")
        route_hosts_with_meal_class = _get_routes_of_cluster_with_meal(final_routes, cluster_12, meal_class)
        sum_meal = len(route_hosts_with_meal_class)
        assert sum_meal == 4

def test_route_building():
    data = load_sample_data("27_teams_017662e4.json")

    routes_of_cluster = _get_routes_of_cluster_with_expected_size(data.get_routes(), 1, 9)

    original_distance_sum = calculate_distance_sum(routes_of_cluster, data.get_distance_matrix())
    print(f"ORIGINAL DISTANCE SUM: {original_distance_sum}")

    _clear_teams_on_route(routes_of_cluster)

    route_builder = RouteBuilder(data, data.get_routes())
    routes_of_cluster, optimized_distance_sum = route_builder.build_route_for_cluster_label(1)

    # Check appetizer hosts
    hosts_appetizer = _get_routes_of_cluster_with_meal(routes_of_cluster, 1, "Vorspeise")
    assert len(hosts_appetizer) == 3
    assert len( set([ h.teamNumber for h in hosts_appetizer ]) ) == 3
    for host_appetizer in hosts_appetizer:
        assert len(host_appetizer.teamsOnRoute) == 2
        visiting_meals = [ other_team_on_route.meal.label for other_team_on_route in host_appetizer.teamsOnRoute ]
        print(f"Asserting {host_appetizer} which visits {host_appetizer.teamsOnRoute} meets constraints")
        assert len(visiting_meals) == 2
        assert set(visiting_meals) == { "Hauptspeise", "Nachspeise" }

    # Check main course hosts
    hosts_main_course = _get_routes_of_cluster_with_meal(routes_of_cluster, 1, "Hauptspeise")
    assert len(hosts_main_course) == 3
    assert len( set([ h.teamNumber for h in hosts_main_course ]) ) == 3
    for host_main_course in hosts_main_course:
        assert len(host_main_course.teamsOnRoute) == 2
        visiting_meals = [ other_team_on_route.meal.label for other_team_on_route in host_main_course.teamsOnRoute ]
        assert len(visiting_meals) == 2
        assert set(visiting_meals) == { "Vorspeise", "Nachspeise" }

    # Check dessert course hosts
    hosts_dessert_course = _get_routes_of_cluster_with_meal(routes_of_cluster, 1, "Nachspeise")
    assert len(hosts_dessert_course) == 3
    assert len( set([ h.teamNumber for h in hosts_dessert_course ]) ) == 3
    for host_dessert_course in hosts_dessert_course:
        assert len(host_dessert_course.teamsOnRoute) == 2
        visiting_meals = [ other_team_on_route.meal.label for other_team_on_route in host_dessert_course.teamsOnRoute ]
        assert len(visiting_meals) == 2
        assert set(visiting_meals) == { "Vorspeise", "Hauptspeise" }

    assert optimized_distance_sum < original_distance_sum, f"Optimized distance sum {optimized_distance_sum} should be less than original {original_distance_sum}"

def _clear_teams_on_route(routes):
    """
    Clears the teamsOnRoute for each route in the cluster.
    """
    for route in routes:
        route.teamsOnRoute = []