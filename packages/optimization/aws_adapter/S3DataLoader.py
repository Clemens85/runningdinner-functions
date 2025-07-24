from loaders.DataLoader import DataLoader
from aws_adapter.S3Client import s3_client

class S3DataLoader(DataLoader):
    def __init__(self, bucket, key):
        self.bucket = bucket
        self.key = key

    def load_json_string(self) -> str:
        obj = s3_client.get_object(Bucket=self.bucket, Key=self.key)
        return obj['Body'].read().decode('utf-8')