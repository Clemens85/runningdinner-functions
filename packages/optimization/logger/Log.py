import os
from logger.LoggerFactory import setup_logger

def is_running_on_lambda():
    return "AWS_LAMBDA_FUNCTION_NAME" in os.environ

Log = setup_logger(local = not is_running_on_lambda())