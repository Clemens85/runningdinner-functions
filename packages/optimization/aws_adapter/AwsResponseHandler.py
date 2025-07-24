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

    def send(self, json_string: str):
        Log.info(f"Sending response with length {len(json_string)} to S3: s3://%s/%s", self.bucket, self.key)
        s3_client.put_object(Bucket=self.bucket, Key=self.key, Body=json_string)
        Log.info("Response sent successfully.")

        message = {
            "bucket": self.bucket,
            "key": self.key,
            "status": "OK"
        }
        Log.info("Publishing message to SNS topic: %s", SNS_TOPIC_ARN)
        Log.info("Message content: %s", message)
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message),
            Subject="Lambda S3 Processing Complete", # TODO
        )


