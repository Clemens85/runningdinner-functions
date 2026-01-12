import os
from ApiKeysSsmFactory import ApiKeysSsmFactory

# Constants for SSM Parameter Store paths
SSM_PARAMETER_PINECONE_API_KEY = "/runningdinner/pinecone/apikey"
SSM_PARAMETER_OPENAI_API_KEY = "/runningdinner/openai/apikey"
SSM_PARAMETER_LANGSMITH_API_KEY = "/runningdinner/langsmith/apikey"

def setup_environment():
  # Get API keys from SSM Parameter Store using batch call for better cold start performance
  api_keys_factory = ApiKeysSsmFactory.get_instance()
  try:
      # Fetch all API keys in a single batch call instead of multiple sequential calls
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