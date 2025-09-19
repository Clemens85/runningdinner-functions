import requests

class RunningDinnerApi:
    def __init__(self, host: str):
        self.host = host

    def get_public_event_info(self, public_event_id: str) -> str:
        url = f"{self.host}/rest/frontend/v1/runningdinner/{public_event_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
        # return RunningDinnerPublicTO(**data)
