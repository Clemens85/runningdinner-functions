from RouteOptimizer import RouteOptimizer
from loaders.LocalFileDataLoader import LocalFileDataLoader
from response.LocalFileResponseHandler import LocalFileResponseHandler
from logger.Log import Log

WORKSPACE_BASE_DIR = "/home/clemens/Projects/runningdinner-functions/packages/optimization/test-data"
file_name = "27_teams_017662e4"

def main():

  request_file_path = f"{WORKSPACE_BASE_DIR}/{file_name}.json"
  response_file_path = f"{WORKSPACE_BASE_DIR}/response/{file_name}.json"
  route_optimizer = RouteOptimizer(LocalFileDataLoader(request_file_path), LocalFileResponseHandler(response_file_path))

  optimized_routes = route_optimizer.optimize()
  Log.info(f"Optimized routes: {optimized_routes}")

if __name__ == "__main__":
    main()