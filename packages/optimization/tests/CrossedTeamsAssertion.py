from typing import Dict

from DinnerRouteList import DinnerRoute

class CrossedTeamsAssertion:
    
    def __init__(self):
      self.crossed_teams_by_team_number: Dict[int, list[DinnerRoute]] = {}

    def record_crossed_teams(self, host_route: DinnerRoute):
        crossed_teams_of_host = self.crossed_teams_by_team_number.get(host_route.teamNumber) or []
        crossed_teams_of_host = crossed_teams_of_host + host_route.teamsOnRoute
        for other_team_on_route in host_route.teamsOnRoute:
            crossed_teams_of_other_team = self.crossed_teams_by_team_number.get(other_team_on_route.teamNumber) or []
            crossed_teams_of_other_team.append(host_route)
            self.crossed_teams_by_team_number[other_team_on_route.teamNumber] = crossed_teams_of_other_team

        self.crossed_teams_by_team_number[host_route.teamNumber] = crossed_teams_of_host

    def assert_no_crossed_teams(self):
        for team_number, crossed_teams in self.crossed_teams_by_team_number.items():
            unique_crossed_teams = set(crossed_teams)
            print(f"Asserting team {team_number} crossed teams: {crossed_teams}")
            assert len(unique_crossed_teams) == len(crossed_teams), f"Team {team_number} has duplicated crossings with these teams: {crossed_teams}"
