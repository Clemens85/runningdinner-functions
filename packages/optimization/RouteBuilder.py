from copy import deepcopy
from typing import List, Dict, Tuple
from logger.Log import Log
from DataProvider import DataProvider
from DinnerRouteList import DinnerRoute, TeamsOnRoute
from MatrixTemplates import get_matrixes_for_cluster_size
import itertools

def calculate_distance_sum(routes: List[DinnerRoute], dist_matrix: List[List[float]]) -> float:
    """
    Calculate the total distance for a list of routes based on the distance matrix.
    """
    total_distance = 0.0
    for route in routes:
        host_index = route.originalIndex
        for team_on_route in route.teamsOnRoute:
            team_on_route_index = [r.originalIndex for r in routes if r.teamNumber == team_on_route.teamNumber][0]
            total_distance += dist_matrix[host_index][team_on_route_index]
    return total_distance

class RouteBuilder:
    def __init__(self, data_provider: DataProvider, routes: List[DinnerRoute]):
        self.routes = deepcopy(routes) # Ensure we don't modify the original DataFrame
        self.dist_matrix = data_provider.get_distance_matrix()
        self.meal_labels = data_provider.get_unique_meal_labels_ordered()  # e.g. ['Vorspeise', 'Hauptspeise', 'Nachspeise']

    def build_route_for_cluster_label(self, cluster_label: int) -> Tuple[List[DinnerRoute], float]:
        """
        Builds a route for a specific cluster label.
        """        
        routes_of_cluster = [route for route in self.routes if route.clusterNumber == cluster_label]
        if not routes_of_cluster:
            raise ValueError(f"No routes found for cluster label {cluster_label}.")
        
        # Get size of cluster_routes dataframe
        cluster_size = len(routes_of_cluster)

        # Get teams grouped by meal class
        teams_by_meal_label = {}
        for meal_label in self.meal_labels:
            teams_by_meal_label[meal_label] = [route for route in routes_of_cluster if route.meal.label == meal_label]

        matrix_list = get_matrixes_for_cluster_size(cluster_size)
        best_matrix: List[List[List[int]]] = []
        best_distance = float('inf')
        best_assignment: Dict[int, DinnerRoute] = {}

        for matrix in matrix_list:
            Log.info(f"Building route for cluster label {cluster_label} with size {cluster_size} and matrix: {matrix}")
            # Find optimal assignment using brute force
            assignment_candidate, distance_sum = self._find_optimal_assignment(teams_by_meal_label, matrix)
            if distance_sum < best_distance:
                best_matrix = matrix
                best_distance = distance_sum
                best_assignment = assignment_candidate

        if len(best_matrix) == 0:
            raise ValueError(f"Unexpected error during route building, no assignment candidate found")

        # Apply the best assignment found
        optimized_routes = self._apply_assignment(best_assignment, best_matrix)
        return optimized_routes, best_distance

    def _find_optimal_assignment(self, teams_by_meal_class: Dict[str, List[DinnerRoute]], matrix: List[List[List[int]]]) -> Tuple[Dict[int, DinnerRoute], float]:
        """
        Find the optimal assignment of teams to matrix positions using brute force.
        :param teams_by_meal_class: Dictionary mapping meal classes to lists of teams.
        :param matrix: The meal arrangement matrix.
        :return: The best assignment of teams to routes.
        """
        best_distance = float('inf')
        best_assignment: Dict[int, DinnerRoute] = None
        
        # Generate all possible permutations for each meal class
        meal_class_permutations: List[List[DinnerRoute]] = []
        for meal_class in self.meal_labels:
            teams = teams_by_meal_class[meal_class]
            meal_class_permutations.append(list(itertools.permutations(teams)))

        Log.info (f"Testing {len(meal_class_permutations)} x {len(meal_class_permutations[0])} meal class permutations")
        
        # Try every combination of permutations
        for permutation_combo in itertools.product(*meal_class_permutations):
            # permutation_combo is something like ( (team v1, team v2, team v3), (team h1, team h2, team h3), (team n1, n2, n3) ) # v=vorspeise, h=hauptspeise, n=nachspeise

            # Create matrix_number_to_team mapping for this permutation
            matrix_number_to_team: Dict[int, DinnerRoute] = {}

            # Assign teams to matrix positions ensuring meal class blocks are respected
            for meal_class_index, meal_class in enumerate(self.meal_labels):
                # permutation_of_meal_class is something like (team1, team2, team3) for 9er matrix
                # but maybe also something like (team1, team2, team3, team4) for 12er matrix
                permutation_of_meal_class = permutation_combo[meal_class_index]
                
                # Each outer row in the matrix represents one hosting meal class block
                # The number of rows in such a block is equal to the number of teams that host this meal class
                # The first number in each row is the host, the rest are guests
                for team_index, team in enumerate(permutation_of_meal_class):
                    matrix_number = matrix[meal_class_index][team_index][0]
                    matrix_number_to_team[matrix_number] = team

                # # Calculate the starting position for this meal class block
                # # Can e.g. be 1 or 4 or 7
                # teams_per_meal = len(permutation_of_meal_class)
                # start_position = meal_class_index * teams_per_meal + 1
                # for team_index, team in enumerate(permutation_of_meal_class):
                #     matrix_position = start_position + team_index
                #     matrix_number_to_team[matrix_position] = team

            # Calculate total distance for this assignment
            total_distance = self._calculate_total_distance(matrix_number_to_team, matrix)
            # print(f"Total distance for current assignment: {total_distance}")
            
            # Keep track of the best assignment
            if total_distance < best_distance:
                best_distance = total_distance
                best_assignment = matrix_number_to_team

        Log.info(f"Best assignment: {best_assignment}")
        return best_assignment, best_distance

    def _calculate_total_distance(self, matrix_number_to_team: Dict[int, DinnerRoute], matrix: List[List[List[int]]]) -> float:
        """
        Calculate the total distance for a given team assignment.
        :param matrix_number_to_team: Mapping from team numbers to DinnerRoute objects.
        :param matrix: The meal arrangement matrix.
        :return: Total distance for the assignment.
        """
        total_distance = 0
        
        # For each meal block in the matrix
        for meal_index, meal_block in enumerate(matrix):
            # For each hosting arrangement in this meal block
            for hosting_arrangement in meal_block:
                # hosting_arrangement is a concrete block, like e.g. [1, 4, 7]
                host_team_number = hosting_arrangement[0]
                guest_team_numbers = hosting_arrangement[1:]
                
                host_route = matrix_number_to_team[host_team_number]
                
                # Calculate distance from host to each guest
                for guest_team_number in guest_team_numbers:
                    guest_route = matrix_number_to_team[guest_team_number]
                    distance = self.dist_matrix[host_route.originalIndex][guest_route.originalIndex]
                    total_distance += distance
        
        return total_distance


    def _apply_assignment(self, matrix_number_to_team: Dict[int, DinnerRoute], matrix: List[List[List[int]]]) -> List[DinnerRoute]:
        """
        Apply the optimal assignment to create the final routes with populated teamsOnRoute.
        """
        # Clear existing teamsOnRoute for all routes
        for route in matrix_number_to_team.values():
            route.teamsOnRoute = []

        # Process each meal block in the matrix
        for meal_index, meal_block in enumerate(matrix):
            # meal_block is a 2d array where each row is like e.g. [ 1, 4, 7 ] whereas 1 represents the hoster of this meal

            # For each hosting arrangement in this meal block
            for hosting_arrangement in meal_block:
                # hosting_arrangement is a concrete block, like e.g. [1, 4, 7]
                host_matrix_number = hosting_arrangement[0]
                host_route = matrix_number_to_team[host_matrix_number]

                team_matrix_numbers_on_route = self._find_team_matrix_numbers_on_route(host_matrix_number, meal_index, matrix)
                for team_matrix_number in team_matrix_numbers_on_route:
                    team_on_route = matrix_number_to_team[team_matrix_number]
                    host_route.teamsOnRoute.append(
                        TeamsOnRoute(
                            teamNumber=team_on_route.teamNumber,
                            teamId=team_on_route.teamId,
                            meal=team_on_route.meal,
                            status=team_on_route.status,
                            geocodingResult=team_on_route.geocodingResult,
                            clusterNumber=team_on_route.clusterNumber,
                            teamsOnRoute=[]
                        )
                    )

        return list(matrix_number_to_team.values())

    def _find_team_matrix_numbers_on_route(self, current_host_matrix_number: int, current_host_meal_index: int, matrix: List[List[List[int]]]) -> List[int]:
        result = []
        # New loop with all meal_blocks of the matrix, except the current one
        for meal_index, meal_block in enumerate(matrix):
            if meal_index == current_host_meal_index:
                continue  # Skip the current meal block
            for hosting_arrangement in meal_block:
                guest_matrix_numbers = hosting_arrangement[1:]
                if current_host_matrix_number in guest_matrix_numbers:
                    result.append(hosting_arrangement[0])

        return result
