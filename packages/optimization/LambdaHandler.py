from RouteOptimizer import RouteOptimizer
from aws_adapter.ResponseKeyMapper import map_response_key
from logger.Log import Log
from aws_lambda_powertools import Tracer, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext
from urllib.parse import unquote_plus

from aws_adapter.AwsResponseHandler import AwsResponseHandler
from aws_adapter.S3DataLoader import S3DataLoader

tracer = Tracer()
metrics = Metrics(namespace="runningdinner-functions", service="route-optimization")

@tracer.capture_lambda_handler
@Log.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, _context: LambdaContext):
    Log.info("Processing event: %s", event)

    for record in event.get("Records", []):
        s3_info = record["s3"]
        source_bucket = s3_info["bucket"]["name"]
        source_key = unquote_plus(s3_info["object"]["key"])

        Log.info(f"Processing file: s3://{source_bucket}/{source_key}")

        try:
            process_single_request(source_bucket, source_key)
        except Exception as e:
            Log.exception("Unhandled exception when procccessing %s", source_key)
            raise e

    # metrics.flush()

def process_single_request(source_bucket: str, source_key: str):
    
    dest_key = map_response_key(source_key)

    data_loader = S3DataLoader(source_bucket, source_key)
    response_handler = AwsResponseHandler(source_bucket, dest_key)

    optimizer = RouteOptimizer(data_loader, response_handler)
    optimizer.optimize()

