from Util import is_running_on_lambda
from logger.LoggerFactory import setup_logger

Log = setup_logger(local = not is_running_on_lambda())