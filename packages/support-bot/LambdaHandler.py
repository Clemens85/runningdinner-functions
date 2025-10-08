from aws_lambda_powertools import Tracer, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext
import json
import os

from langsmith import traceable
from langsmith.wrappers import OpenAIAgentsTracingProcessor
from agents import set_trace_processors

from logger.Log import Log
from UserRequest import UserRequest
from memory.MemoryProvider import MemoryProvider
from pinecone_db.PineconeDbRepository import PineconeDbRepository
from SupportRequestHandler import SupportRequestHandler
from ApiKeysSsmFactory import ApiKeysSsmFactory

from HttpUtil import get_http_method, is_http_path_match

# Initialize tools
tracer = Tracer()
metrics = Metrics(namespace="runningdinner-functions", service="support-bot")

# Constants for SSM Parameter Store paths
SSM_PARAMETER_PINECONE_API_KEY = "/runningdinner/pinecone/apikey"
SSM_PARAMETER_OPENAI_API_KEY = "/runningdinner/openai/apikey"
SSM_PARAMETER_LANGSMITH_API_KEY = "/runningdinner/langsmith/apikey"

# Get API keys from SSM Parameter Store using batch call for better cold start performance
api_keys_factory = ApiKeysSsmFactory.get_instance()
try:
    # Fetch all API keys in a single batch call instead of 3 sequential calls
    api_keys = api_keys_factory.get_api_keys_batch([
        SSM_PARAMETER_PINECONE_API_KEY,
        SSM_PARAMETER_OPENAI_API_KEY,
        SSM_PARAMETER_LANGSMITH_API_KEY
    ])
    os.environ["PINECONE_API_KEY"] = api_keys[SSM_PARAMETER_PINECONE_API_KEY]
    os.environ["OPENAI_API_KEY"] = api_keys[SSM_PARAMETER_OPENAI_API_KEY]
    os.environ["LANGSMITH_API_KEY"] = api_keys[SSM_PARAMETER_LANGSMITH_API_KEY]
except Exception as e:
    raise EnvironmentError(f"Failed to retrieve API keys from SSM Parameter Store: {str(e)}")

set_trace_processors([OpenAIAgentsTracingProcessor()])

vector_db_repository = PineconeDbRepository()
memory_provider = MemoryProvider()
support_request_handler = SupportRequestHandler(memory_provider=memory_provider, vector_db_repository=vector_db_repository)

@tracer.capture_lambda_handler
@Log.inject_lambda_context(log_event=True)
@traceable
def lambda_handler(event: dict, context: LambdaContext):

    Log.info("Processing event: %s", event)

    if is_http_path_match(event, "/warmup") and get_http_method(event) == "GET":
        return support_request_handler.warm_up()

    try:
        http_body_str = event['body']
        http_body = json.loads(http_body_str)
        user_request = UserRequest(**http_body)
        return support_request_handler.process_user_request(user_request)
    except Exception as e:
        Log.exception("Unhandled exception when processing request %s", str(e))
        return support_request_handler.process_error(e)
