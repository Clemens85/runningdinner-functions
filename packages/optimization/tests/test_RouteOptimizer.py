from typing import Dict

from RouteOptimizer import RouteOptimizer
from local_adapter.LocalFileDataLoader import LocalFileDataLoader
from response.ResponseHandler import ResponseHandler

WORKSPACE_BASE_DIR = 'test-data'

class InMemoryResponseHandler(ResponseHandler):
    def __init__(self):
        self.json_payloads = []
        self.finished_events = []

    def send(self, json_payload: str, finished_event: Dict[str, any]):
        self.json_payloads.append(json_payload)
        self.finished_events.append(finished_event)

def test_exception_handling():
  test_response_handler = InMemoryResponseHandler()
  route_optimizer = RouteOptimizer(data_loader=LocalFileDataLoader(f'{WORKSPACE_BASE_DIR}/corrupted_data.json'), response_handler=test_response_handler)
  try:
    route_optimizer.optimize()
    assert False, "Expected exception was not raised"
  except Exception as e:
    assert len(test_response_handler.json_payloads) == 1
    assert len(test_response_handler.finished_events) == 1
    assert test_response_handler.finished_events[0]['adminId'] == route_optimizer.data.get_admin_id()
    assert test_response_handler.finished_events[0]['optimizationId'] == route_optimizer.data.get_optimization_id()
    assert len(test_response_handler.finished_events[0]['errorMessage']) > 0
    assert test_response_handler.json_payloads[0] == '{"errorMessage": "list index out of range"}'

def test_route_optimizer_with_valid_data():
    test_response_handler = InMemoryResponseHandler()
    route_optimizer = RouteOptimizer(data_loader=LocalFileDataLoader(f'{WORKSPACE_BASE_DIR}/27_teams.json'), response_handler=test_response_handler)
    optimized_routes, optimized_distance = route_optimizer.optimize()
    assert optimized_routes is not None
    assert optimized_distance is not None
    assert len(optimized_routes) == 27
    assert optimized_distance > 0

    assert len(test_response_handler.json_payloads) > 0
    assert len(test_response_handler.finished_events) > 0
    assert test_response_handler.finished_events[0]['adminId'] == route_optimizer.data.get_admin_id()
    assert test_response_handler.finished_events[0]['optimizationId'] == route_optimizer.data.get_optimization_id()
    assert '"dinnerRoutes": [' in test_response_handler.json_payloads[0]