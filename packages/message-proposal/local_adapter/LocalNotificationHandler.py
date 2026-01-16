from typing import List

from NotificationHandler import NotificationHandler

class LocalNotificationHandler(NotificationHandler):
    def __init__(self):
        self.messages: List[str] = []

    def send_notification(self, message: str):
        self.messages.append(message)

    def get_messages(self) -> List[str]:
        return self.messages