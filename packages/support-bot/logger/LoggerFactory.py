from aws_lambda_powertools import Logger

def setup_logger(local: bool = False) -> Logger:
    if local:
        # Human-readable logs for local runs
        logger = Logger(service="support-bot")
    else:
        # Structured logs for Lambda
        logger = Logger(service="support-bot")
    return logger