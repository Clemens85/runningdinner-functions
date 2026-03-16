import os
from response.OptimizationEvent import OptimizationEvent
from response.ResponseHandler import ResponseHandler
from aws_adapter.S3Client import s3_client
from aws_adapter.SNSClient import sns_client
from logger.Log import Log

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
SNS_ERROR_TOPIC_ARN = os.environ.get("SNS_ERROR_TOPIC_ARN")

class AwsResponseHandler(ResponseHandler):
    def __init__(self, bucket, key):
        self.bucket = bucket
        self.key = key

    def send(self, json_string: str, finished_event: OptimizationEvent):
        Log.info(f"Sending response with length {len(json_string)} to S3: s3://%s/%s", self.bucket, self.key)
        s3_client.put_object(Bucket=self.bucket, Key=self.key, Body=json_string)
        Log.info("Response sent successfully.")

        message_payload = finished_event.model_dump_json(exclude_none=True)

        Log.info("Publishing message to SNS topic: %s", SNS_TOPIC_ARN)
        Log.info("Message content: %s", message_payload)

        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message_payload,
            Subject="Optimization Finished"
        )

        if finished_event.errorMessage and SNS_ERROR_TOPIC_ARN:
            Log.info("Publishing error alert to SNS error topic: %s", SNS_ERROR_TOPIC_ARN)
            sns_client.publish(
                TopicArn=SNS_ERROR_TOPIC_ARN,
                Message=message_payload,
                Subject=f"Route Optimization Error [{finished_event.adminId}]"
            )


