import os
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from RouteOptimizer import RouteOptimizer
from local_adapter.LocalFileDataLoader import LocalFileDataLoader
from local_adapter.LocalFileResponseHandler import LocalFileResponseHandler
from logger.Log import Log

WORKSPACE_BASE_DIR = "/home/clemens/Projects/runningdinner-functions/packages/optimization/test-data"

REQUEST_PATTERN = re.compile(r"(?P<optimization_id>.+)-request\.json$")

class RequestFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        rel_path = os.path.relpath(event.src_path, WORKSPACE_BASE_DIR)
        parts = rel_path.split(os.sep)
        if len(parts) >= 3 and parts[0] == "optimization":
            admin_id = parts[1]
            filename = parts[2]
            match = REQUEST_PATTERN.match(filename)
            if match:
                optimization_id = match.group("optimization_id")
                request_file_path = event.src_path
                response_file_path = os.path.join(
                    WORKSPACE_BASE_DIR, "optimization", admin_id, f"{optimization_id}-response.json"
                )
                Log.info(f"Detected new request: {request_file_path}")
                route_optimizer = RouteOptimizer(
                    LocalFileDataLoader(request_file_path),
                    LocalFileResponseHandler(response_file_path)
                )
                optimized_routes = route_optimizer.optimize()
                Log.info(f"Optimized routes: {optimized_routes}")

def main():
    observer = Observer()
    event_handler = RequestFileHandler()
    observer.schedule(event_handler, WORKSPACE_BASE_DIR, recursive=True)
    observer.start()
    Log.info("Watching for new request files...")
    try:
        while True:
            pass  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()