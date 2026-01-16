import os

from NotificationHandler import NotificationHandler
from aws_adapter.SNSClient import sns_client
from logger.Log import logger

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

class SNSNotificationHandler(NotificationHandler):
    def send_notification(self, message: str):
        logger.info("Publishing message to SNS topic: %s", SNS_TOPIC_ARN)
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="Generated Message Proposal(s)"
        )
