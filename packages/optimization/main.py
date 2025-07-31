from RouteOptimizer import RouteOptimizer
from local_adapter.LocalFileDataLoader import LocalFileDataLoader
from local_adapter.LocalFileResponseHandler import LocalFileResponseHandler
from logger.Log import Log

WORKSPACE_BASE_DIR = "/home/clemens/Projects/runningdinner-functions/packages/optimization/test-data"
# file_name = "27_teams_017662e4"
# request_file_path = f"{WORKSPACE_BASE_DIR}/{file_name}.json"
# response_file_path = f"{WORKSPACE_BASE_DIR}/response/{file_name}.json"

admin_id = "a9715776-7298-4afe-a2ce-aa6ec6207f96-3aPBq"
optimization_id = "66d52cdf"
request_file_path = f"{WORKSPACE_BASE_DIR}/{admin_id}/optimization/request-{optimization_id}.json"
response_file_path = f"{WORKSPACE_BASE_DIR}/{admin_id}/optimization/response-{optimization_id}.json"

def main():
    route_optimizer = RouteOptimizer(LocalFileDataLoader(request_file_path), LocalFileResponseHandler(response_file_path))

    optimized_routes = route_optimizer.optimize()
    Log.info(f"Optimized routes: {optimized_routes}")


if __name__ == "__main__":
    main()
