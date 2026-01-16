from abc import ABC, abstractmethod
from typing import List
from ExampleMessage import ExampleMessage

class NotificationHandler(ABC):
    @abstractmethod
    def send_notification(self, message: str) -> str:
        pass

    def build_notification_message(self, generated_messages: List[ExampleMessage]) -> str:
        if not generated_messages or len(generated_messages) == 0:
            return "No message proposals were generated."

        event_description = generated_messages[0].event_description
        message_lines = ["The following message proposals have been generated:\n",
                         f"Based on Event Description:\n{event_description}\n\n"]
        for gen_msg in generated_messages:
            message_lines.append(f"- Type: {gen_msg.type}, Message Preview: {gen_msg.message[:2000]}...\n")
        return "".join(message_lines)
    