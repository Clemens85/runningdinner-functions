import json
import os
from response.ResponseHandler import ResponseHandler
from aws_adapter.S3Client import s3_client
from aws_adapter.SNSClient import sns_client
from logger.Log import Log

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

class AwsResponseHandler(ResponseHandler):
    def __init__(self, bucket, key):
        self.bucket = bucket
        self.key = key

    def send(self, json_string: str, finished_event: dict):
        Log.info(f"Sending response with length {len(json_string)} to S3: s3://%s/%s", self.bucket, self.key)
        s3_client.put_object(Bucket=self.bucket, Key=self.key, Body=json_string)
        Log.info("Response sent successfully.")

        message_payload = json.dumps(finished_event)

        Log.info("Publishing message to SNS topic: %s", SNS_TOPIC_ARN)
        Log.info("Message content: %s", message_payload)
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message_payload,
            Subject="Optimization Finished"
        )


