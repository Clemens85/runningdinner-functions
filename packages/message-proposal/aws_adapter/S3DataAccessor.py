from aws_adapter.S3Client import s3_client
from ..DataAccessor import DataAccessor

class S3DataAccessor(DataAccessor):
    def __init__(self, bucket):
        self.bucket = bucket

    def load_string(self, storage_path: str) -> str:
        obj = s3_client.get_object(Bucket=self.bucket, Key=storage_path)
        return obj['Body'].read().decode('utf-8')
    
    def write_string_to_path(self, content: str, storage_path: str):
        s3_client.put_object(Bucket=self.bucket, Key=storage_path, Body=content.encode('utf-8'))

