from RouteOptimizer import RouteOptimizer
from local_adapter.LocalFileDataLoader import LocalFileDataLoader
from local_adapter.LocalFileResponseHandler import LocalFileResponseHandler
from logger.Log import Log

WORKSPACE_BASE_DIR = "/home/clemens/Projects/runningdinner-functions/packages/optimization/test-data"

admin_id = "__ADMIN_ID__"
optimization_id = "__OPTIMIZATION_ID__"
request_file_path = f"{WORKSPACE_BASE_DIR}/optimization/{admin_id}/{optimization_id}-request.json"
response_file_path = f"{WORKSPACE_BASE_DIR}/optimization/{admin_id}/{optimization_id}-response.json"

def main():
    route_optimizer = RouteOptimizer(LocalFileDataLoader(request_file_path), LocalFileResponseHandler(response_file_path))

    optimized_routes = route_optimizer.optimize()
    Log.info(f"Optimized routes: {optimized_routes}")


if __name__ == "__main__":
    main()
