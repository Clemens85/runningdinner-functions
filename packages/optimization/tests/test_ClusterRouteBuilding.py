from collections import Counter
from itertools import permutations, product
from pathlib import Path
from typing import List

from DefaultClusterer import DefaultClusterer
from DataProvider import DataProvider
from DinnerRouteList import DinnerRoute, RouteOptimizationSettings
from MatrixTemplates import get_matrixes_for_cluster_size, matrix9_1, matrix9_2
from RouteBuilder import calculate_distance_sum
from RouteBuilder import RouteBuilder
from local_adapter.LocalFileDataLoader import LocalFileDataLoader
from tests.CrossedTeamsAssertion import CrossedTeamsAssertion

import pytest

WORKSPACE_BASE_DIR = test_dir = Path(__file__).parent.parent / "test-data"
WORKSPACE_BASE_DIR = WORKSPACE_BASE_DIR.resolve()

IGNORE_MEAL_ASSIGNMENTS: RouteOptimizationSettings = RouteOptimizationSettings(
    currentSumDistanceInMeters=0,
    currentAverageDistanceInMeters=0,
    ignoreMealAssignments=True,
    minimumDistanceInMeters=0
)
KEEP_MEAL_ASSIGNMENTS: RouteOptimizationSettings = RouteOptimizationSettings(
    currentSumDistanceInMeters=0,
    currentAverageDistanceInMeters=0,
    ignoreMealAssignments=False,
    minimumDistanceInMeters=0
)
MINIMUM_DISTANCE: RouteOptimizationSettings = RouteOptimizationSettings(
    currentSumDistanceInMeters=0,
    currentAverageDistanceInMeters=0,
    ignoreMealAssignments=False,
    minimumDistanceInMeters=1800
)

def load_sample_data(filename: str, optimization_settings: RouteOptimizationSettings) -> DataProvider:
  data = DataProvider(LocalFileDataLoader(f'{WORKSPACE_BASE_DIR}/{filename}'))
  data.optimization_settings = optimization_settings
  return data

def _get_routes_of_cluster_with_expected_size(routes, cluster_label, expected_size):
    print(f"Asserting cluster {cluster_label} has {expected_size} items")
    result = [route for route in routes if route.clusterNumber == cluster_label]
    assert len(result) == expected_size
    return result

def _get_routes_of_cluster_with_meal(routes: List[DinnerRoute], cluster_label: int, meal_label: str):
    result = [route for route in routes if route.clusterNumber == cluster_label]
    result = [route for route in result if route.meal.label == meal_label]
    return result

@pytest.mark.parametrize("optimization_settings", [
    pytest.param(KEEP_MEAL_ASSIGNMENTS, id="KEEP_MEAL_ASSIGNMENTS"),
    pytest.param(IGNORE_MEAL_ASSIGNMENTS, id="IGNORE_MEAL_ASSIGNMENTS"),
    pytest.param(MINIMUM_DISTANCE, id="MINIMUM_DISTANCE")
])
def test_predict_3_team_clusters(optimization_settings: RouteOptimizationSettings):
    data = load_sample_data("27_teams.json", optimization_settings=optimization_settings)

    assert data.get_cluster_template()[0] == ['Vorspeise', 'Vorspeise', 'Vorspeise', 'Hauptspeise', 'Hauptspeise', 'Hauptspeise', 'Nachspeise', 'Nachspeise', 'Nachspeise']

    clusterer = DefaultClusterer(data)
    final_routes, final_labels = clusterer.predict()
    assert len(final_routes) == 27
    assert len(final_labels) == 27
    assert set(final_labels) == {0, 1, 2}

    for cluster_label in range (3):
        routes_of_cluster = _get_routes_of_cluster_with_expected_size(final_routes, cluster_label, 9)
        for meal_label in (["Vorspeise", "Hauptspeise", "Nachspeise"]):
          print (f"Asserting cluster {cluster_label} has 3 occurrences of {meal_label}")
          sum_meal = len([route for route in routes_of_cluster if route.meal.label == meal_label])
          assert sum_meal == 3

@pytest.mark.parametrize("optimization_settings", [
    pytest.param(KEEP_MEAL_ASSIGNMENTS, id="KEEP_MEAL_ASSIGNMENTS"),
    pytest.param(IGNORE_MEAL_ASSIGNMENTS, id="IGNORE_MEAL_ASSIGNMENTS"),
    pytest.param(MINIMUM_DISTANCE, id="MINIMUM_DISTANCE")
])
def test_predict_5_team_clusters(optimization_settings: RouteOptimizationSettings):
    data = load_sample_data("45_teams.json", optimization_settings=optimization_settings)

    clusterer = DefaultClusterer(data)
    num_expected_clusters = len(data.get_cluster_sizes())
    assert num_expected_clusters == 5

    final_routes, final_labels = clusterer.predict()
    assert len(final_labels) == 45
    assert set(final_labels) == {0, 1, 2, 3, 4}

    for cluster_label in range (5):
        routes_of_cluster = _get_routes_of_cluster_with_expected_size(final_routes, cluster_label, 9)
        for meal_label in (["Vorspeise", "Hauptspeise", "Nachspeise"]):
          print (f"Asserting cluster {cluster_label} has 3 occurrences of {meal_label}")
          sum_meal = len([route for route in routes_of_cluster if route.meal.label == meal_label])
          assert sum_meal == 3

@pytest.mark.parametrize("optimization_settings", [
    pytest.param(KEEP_MEAL_ASSIGNMENTS, id="KEEP_MEAL_ASSIGNMENTS"),
    pytest.param(IGNORE_MEAL_ASSIGNMENTS, id="IGNORE_MEAL_ASSIGNMENTS"),
    pytest.param(MINIMUM_DISTANCE, id="MINIMUM_DISTANCE")
])
def test_predict_2_team_clusters_different_sizes(optimization_settings: RouteOptimizationSettings):
    data = load_sample_data("21_teams.json", optimization_settings=optimization_settings)

    clusterer = DefaultClusterer(data)
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
    for _, meal_label in enumerate(["Vorspeise", "Hauptspeise", "Nachspeise"]):
        print(f"Asserting cluster {cluster_9} has 3 occurrences of {meal_label}")
        route_hosts_with_meal_class = _get_routes_of_cluster_with_meal(final_routes, cluster_9, meal_label)
        sum_meal = len(route_hosts_with_meal_class)
        assert sum_meal == 3

    cluster_12 = unique_cluster_labels[1]
    cluster_12_routes = _get_routes_of_cluster_with_expected_size(final_routes, cluster_12, 12)
    for _, meal_label in enumerate(["Vorspeise", "Hauptspeise", "Nachspeise"]):
        print(f"Asserting cluster {cluster_12} has 4 occurrences of {meal_label}")
        route_hosts_with_meal_class = _get_routes_of_cluster_with_meal(final_routes, cluster_12, meal_label)
        sum_meal = len(route_hosts_with_meal_class)
        assert sum_meal == 4

    _clear_teams_on_route(cluster_12_routes)

    route_builder = RouteBuilder(data, data.get_routes())
    routes_of_cluster, _ = route_builder.build_route_for_cluster_label(2)
    assert_routes_of_cluster(routes_of_cluster, cluster_label=2, expected_meals_size=4)

@pytest.mark.parametrize("optimization_settings", [
    pytest.param(KEEP_MEAL_ASSIGNMENTS, id="KEEP_MEAL_ASSIGNMENTS"),
    pytest.param(IGNORE_MEAL_ASSIGNMENTS, id="IGNORE_MEAL_ASSIGNMENTS"),
    pytest.param(MINIMUM_DISTANCE, id="MINIMUM_DISTANCE")
])
def test_predict_only_one_cluster(optimization_settings: RouteOptimizationSettings):
    data = load_sample_data("15_teams.json", optimization_settings=optimization_settings)

    clusterer = DefaultClusterer(data)
    num_expected_clusters = len(data.get_cluster_sizes())
    assert num_expected_clusters == 1

    final_routes, final_labels = clusterer.predict()
    assert len(final_labels) == 15
    assert set(final_labels) == {0}

    routes_of_cluster = _get_routes_of_cluster_with_expected_size(final_routes, 0, 15)
    for meal_label in (["Vorspeise", "Hauptspeise", "Nachspeise"]):
        print(f"Asserting cluster 0 has 5 occurrences of {meal_label}")
        sum_meal = len([route for route in routes_of_cluster if route.meal.label == meal_label])
        assert sum_meal == 5

def test_route_building():
    data = load_sample_data("27_teams.json", optimization_settings=KEEP_MEAL_ASSIGNMENTS)

    for cluster_index in range(3):
        cluster_label = cluster_index + 1

        routes_of_cluster = _get_routes_of_cluster_with_expected_size(data.get_routes(), cluster_label, 9)

        original_distance_sum = calculate_distance_sum(routes_of_cluster, data.get_distance_matrix())
        print(f"ORIGINAL DISTANCE SUM: {original_distance_sum}")

        _clear_teams_on_route(routes_of_cluster)

        route_builder = RouteBuilder(data, data.get_routes())
        routes_of_cluster, optimized_distance_sum = route_builder.build_route_for_cluster_label(cluster_label)
        print(f"OPTIMIZED DISTANCE SUM: {optimized_distance_sum}")
        assert_routes_of_cluster(routes_of_cluster, cluster_label=cluster_label, expected_meals_size=3)
        assert optimized_distance_sum < original_distance_sum, f"Optimized distance sum {optimized_distance_sum} should be less than original {original_distance_sum}"

@pytest.mark.parametrize("optimization_settings", [
    pytest.param(KEEP_MEAL_ASSIGNMENTS, id="KEEP_MEAL_ASSIGNMENTS"),
    pytest.param(IGNORE_MEAL_ASSIGNMENTS, id="IGNORE_MEAL_ASSIGNMENTS"),
    pytest.param(MINIMUM_DISTANCE, id="MINIMUM_DISTANCE")
])
def test_predict_1_team_cluster_15_teams(optimization_settings: RouteOptimizationSettings):
    data = load_sample_data("15_teams.json", optimization_settings=optimization_settings)

    clusterer = DefaultClusterer(data)
    num_expected_clusters = len(data.get_cluster_sizes())
    assert num_expected_clusters == 1

    final_routes, final_labels = clusterer.predict()
    assert len(final_labels) == 15
    assert set(final_labels) == {0}

    routes_of_cluster = _get_routes_of_cluster_with_expected_size(final_routes, 0, 15)
    for meal_label in (["Vorspeise", "Hauptspeise", "Nachspeise"]):
        print(f"Asserting cluster 0 has 5 occurrences of {meal_label}")
        sum_meal = len([route for route in routes_of_cluster if route.meal.label == meal_label])
        assert sum_meal == 5

    route_builder = RouteBuilder(data, routes_of_cluster)
    routes_of_cluster, _ = route_builder.build_route_for_cluster_label(0)

    assert_routes_of_cluster(routes_of_cluster, cluster_label=0, expected_meals_size=5)


def _count_inaccessible_route_visits(routes: List[DinnerRoute]) -> int:
    hosts_by_number = {route.teamNumber: route for route in routes}
    return sum(
        not hosts_by_number[host.teamNumber].isHomeAccessible
        for route in routes if route.requiresAccessibleHome
        for host in route.teamsOnRoute
    )


@pytest.mark.parametrize("requiring_positions, accessible_positions", [
    pytest.param([], [], id="no_requirements"),
    pytest.param([0], list(range(1, 9)), id="requiring_home_need_not_be_accessible"),
    pytest.param([0], [3], id="partially_fulfillable"),
    pytest.param([0], [], id="unfulfillable"),
    pytest.param(list(range(9)), [0, 3, 6], id="competing_requirements"),
])
def test_route_building_accessibility(requiring_positions, accessible_positions):
    data = load_sample_data("27_teams.json", optimization_settings=KEEP_MEAL_ASSIGNMENTS)
    meal_labels = data.get_unique_meal_labels_ordered()
    routes = [route for route in data.get_routes() if route.clusterNumber == 1]
    routes = [route for meal in meal_labels for route in routes if route.meal.label == meal]
    for position, route in enumerate(routes):
        route.requiresAccessibleHome = position in requiring_positions
        route.isHomeAccessible = position in accessible_positions
    original_routes = [route.model_dump() for route in routes]
    distances = data.get_distance_matrix()
    expected_score = (float('inf'), float('inf'))

    for matrix in get_matrixes_for_cluster_size(9):
        meal_permutations = [permutations([route for route in routes if route.meal.label == meal]) for meal in meal_labels]
        for combination in product(*meal_permutations):
            assignment = {
                arrangement[0]: team
                for meal_block, teams in zip(matrix, combination)
                for arrangement, team in zip(meal_block, teams)
            }
            visits = [
                (assignment[guest_number], assignment[arrangement[0]])
                for meal_block in matrix
                for arrangement in meal_block
                for guest_number in arrangement[1:]
            ]
            score = (
                sum(guest.requiresAccessibleHome and not host.isHomeAccessible for guest, host in visits),
                sum(distances[host.originalIndex][guest.originalIndex] for guest, host in visits),
            )
            expected_score = min(expected_score, score)

    optimized_routes, distance = RouteBuilder(data, routes).build_route_for_cluster_label(1)

    assert (_count_inaccessible_route_visits(optimized_routes), distance) == expected_score
    assert distance == pytest.approx(calculate_distance_sum(optimized_routes, distances))
    assert_routes_of_cluster(optimized_routes, cluster_label=1, expected_meals_size=3)
    assert [route.model_dump() for route in routes] == original_routes
    assert {
        route.teamNumber: (route.requiresAccessibleHome, route.isHomeAccessible, route.originalIndex)
        for route in optimized_routes
    } == {
        route.teamNumber: (route.requiresAccessibleHome, route.isHomeAccessible, route.originalIndex)
        for route in routes
    }


def test_route_building_prefers_accessibility_across_templates(monkeypatch):
    data = load_sample_data("27_teams.json", optimization_settings=KEEP_MEAL_ASSIGNMENTS)
    routes = [route for route in data.get_routes() if route.clusterNumber == 1]
    builder = RouteBuilder(data, routes)
    assignment = {
        arrangement[0]: team
        for meal_label, meal_block in zip(builder.meal_labels, matrix9_1)
        for arrangement, team in zip(meal_block, [route for route in builder.routes if route.meal.label == meal_label])
    }
    assignment[1].requiresAccessibleHome = True
    assignment[6].isHomeAccessible = True
    assignment[9].isHomeAccessible = True
    monkeypatch.setattr("RouteBuilder.get_matrixes_for_cluster_size", lambda size: [matrix9_2, matrix9_1])
    monkeypatch.setattr(builder, "_find_optimal_assignment", lambda teams, matrix: (assignment, 100.0 if matrix is matrix9_1 else 1.0))

    optimized_routes, distance = builder.build_route_for_cluster_label(1)

    assert _count_inaccessible_route_visits(optimized_routes) == 0
    assert distance == 100.0


def assert_routes_of_cluster(routes_of_cluster: List[DinnerRoute], cluster_label: int, expected_meals_size: int):
    crossed_teams_assertion = CrossedTeamsAssertion()
    meal_courses = {
        "Vorspeise": {"Hauptspeise", "Nachspeise"},
        "Hauptspeise": {"Vorspeise", "Nachspeise"},
        "Nachspeise": {"Vorspeise", "Hauptspeise"}
    }
    for meal, expected_visiting_meals in meal_courses.items():
        hosts_of_meal = _get_routes_of_cluster_with_meal(routes_of_cluster, cluster_label, meal)
        assert len(hosts_of_meal) == expected_meals_size
        assert len(set([h.teamNumber for h in hosts_of_meal])) == expected_meals_size
        for host_of_meal in hosts_of_meal:
            assert len(host_of_meal.teamsOnRoute) == 2
            visiting_meals = {other_team_on_route.meal.label for other_team_on_route in host_of_meal.teamsOnRoute}
            print(f"Asserting {host_of_meal} which visits {host_of_meal.teamsOnRoute} meets constraints")
            assert len(visiting_meals) == 2
            assert visiting_meals == expected_visiting_meals
            crossed_teams_assertion.record_crossed_teams(host_of_meal)
        print(f"Asserting no crossed for teams hosting {meal}")
        crossed_teams_assertion.assert_no_crossed_teams()


def _clear_teams_on_route(routes):
    """
    Clears the teamsOnRoute for each route in the cluster.
    """
    for route in routes:
        route.teamsOnRoute = []