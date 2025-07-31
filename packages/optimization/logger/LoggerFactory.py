from aws_lambda_powertools import Logger

def setup_logger(local: bool = False) -> Logger:
    if local:
        # Human-readable logs for local runs
        logger = Logger(service="route-optimization")
    else:
        # Structured logs for Lambda
        logger = Logger(service="route-optimization")
    return logger