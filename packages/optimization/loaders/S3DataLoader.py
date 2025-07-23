import boto3

from loaders.DataLoader import DataLoader

class S3DataLoader(DataLoader):
    def __init__(self, bucket, key):
        self.bucket = bucket
        self.key = key

    def load_json_string(self) -> str:
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=self.bucket, Key=self.key)
        return obj['Body'].read().decode('utf-8')