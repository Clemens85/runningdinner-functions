import json
from response.ResponseHandler import ResponseHandler
import requests

class LocalFileResponseHandler(ResponseHandler):
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.notification_url = "http://localhost:9090/rest/sse/v1/dinnerroute/optimization/notify"

    def send(self, json_string: str, finished_event: dict):
        with open(self.file_path, 'w') as f:
            f.write(json_string)
            f.flush()
            f.close()

        self._send_notification_response(finished_event)

    def _send_notification_response(self, finished_event: dict):
        # admin_id, optimization_id = self._parse_ids_from_response_path()
        print (f"Sending notification response to {self.notification_url} for finished event {finished_event}")

        headers = {
            "Content-Type": "text/plain"
        }

        # Wrap payload as SNS message
        sns_message = {
            "Type": "Notification",
            "MessageId": finished_event.get("optimizatinId"),
            "TopicArn": "arn:aws:sns:region:eu-central-1:local-python-code",
            "Subject": "OptimizationNotification",
            "Message": json.dumps(finished_event),
            "Timestamp": "2025-07-29T12:00:00.000Z"
        }

        response = requests.post(self.notification_url, json=sns_message, headers=headers)
        print(response.status_code)
        print(response.text)
