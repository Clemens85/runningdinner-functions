APPLICATION_JSON = "application/json"

def get_http_method(event: dict) -> str:
    return (
        event.get("requestContext", {})
             .get("http", {})
             .get("method")
        or event.get("httpMethod")
    )

def get_http_path(event: dict) -> str:
    return (
        event.get("rawPath")
        or event.get("requestContext", {})
                 .get("http", {})
                 .get("path")
        or event.get("path")
    )

def is_http_path_match(event: dict, target_path: str) -> bool:
    path = get_http_path(event)
    return path == target_path or path == f"{target_path}/"