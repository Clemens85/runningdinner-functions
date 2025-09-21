from aws_lambda_powertools import Tracer, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import content_types
import json
import os
from logger.Log import Log
from UserRequest import UserRequest
from memory.MemoryProvider import MemoryProvider
from pinecone_db.PineconeDbRepository import PineconeDbRepository
from SupportRequestHandler import SupportRequestHandler
from ApiKeysSsmFactory import ApiKeysSsmFactory

# Initialize tools
tracer = Tracer()
metrics = Metrics(namespace="runningdinner-functions", service="support-bot")

# Constants for SSM Parameter Store paths
SSM_PARAMETER_PINECONE_API_KEY = "/runningdinner/pinecone/apikey"
SSM_PARAMETER_OPENAI_API_KEY = "/runningdinner/openai/apikey"

# Get API keys from SSM Parameter Store
api_keys_factory = ApiKeysSsmFactory.get_instance()
try:
    os.environ["PINECONE_API_KEY"] = api_keys_factory.get_api_key(SSM_PARAMETER_PINECONE_API_KEY)
    os.environ["OPENAI_API_KEY"] = api_keys_factory.get_api_key(SSM_PARAMETER_OPENAI_API_KEY)
except Exception as e:
    raise EnvironmentError(f"Failed to retrieve API keys from SSM Parameter Store: {str(e)}")

vector_db_repository = PineconeDbRepository()
memory_provider = MemoryProvider()
support_reqquest_handler = SupportRequestHandler(memory_provider=memory_provider, vector_db_repository=vector_db_repository)

@tracer.capture_lambda_handler
@Log.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext):

    Log.info("Processing event: %s", event)

    try:
        http_body_str = event['body']
        http_body = json.loads(http_body_str)
        user_request = UserRequest(**http_body)
        return support_reqquest_handler.process_user_request(user_request)
    except Exception as e:
        Log.exception("Unhandled exception when processing request %s", str(e))
        return support_reqquest_handler.process_error(e)
