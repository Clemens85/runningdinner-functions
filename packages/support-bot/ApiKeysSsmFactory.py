import boto3
from aws_lambda_powertools import Logger
from typing import Dict, Optional
import threading

# Create a logger
logger = Logger(service="ApiKeysSsmFactory")

class ApiKeysSsmFactory:
    """
    Factory class for retrieving API keys from AWS SSM Parameter Store with caching.
    Implements the Singleton pattern to ensure only one instance exists.
    """
    _instance = None
    _lock = threading.Lock()  # Lock for thread safety

    def __new__(cls):
        """Singleton implementation"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ApiKeysSsmFactory, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # Initialize SSM client
        self._ssm_client = boto3.client('ssm')
        # Cache for API keys
        self._cached_parameters: Dict[str, str] = {}
        # Flag to track initialization
        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'ApiKeysSsmFactory':
        """Get the singleton instance"""
        return cls()

    def get_api_key(self, parameter_name: str, with_decryption: bool = True) -> str:
        """
        Get an API key from SSM Parameter Store with caching.
        
        Args:
            parameter_name: The name of the parameter in SSM
            with_decryption: Whether to decrypt the parameter value
            
        Returns:
            The parameter value as a string
            
        Raises:
            Exception: If the parameter cannot be retrieved or doesn't exist
        """
        # Return from cache if available
        if parameter_name in self._cached_parameters:
            return self._cached_parameters[parameter_name]
            
        # Fetch from SSM if not in cache
        try:
            return self._fetch_and_cache_parameter(parameter_name, with_decryption)
        except Exception as e:
            # Retry once on failure
            logger.warning(f"Failed to fetch parameter {parameter_name}, retrying: {str(e)}")
            try:
                return self._fetch_and_cache_parameter(parameter_name, with_decryption)
            except Exception as inner_e:
                error_message = f"Failed to fetch SSM parameter ({parameter_name}): {str(inner_e)}"
                logger.error(error_message)
                raise Exception(error_message)

    def get_api_keys_batch(self, parameter_names: list[str], with_decryption: bool = True) -> Dict[str, str]:
        """
        Get multiple API keys from SSM Parameter Store in a single batch call with caching.
        This is more efficient than multiple individual get_api_key calls, especially during Lambda cold starts.
        
        Args:
            parameter_names: List of parameter names in SSM
            with_decryption: Whether to decrypt the parameter values
            
        Returns:
            Dictionary mapping parameter names to their values
            
        Raises:
            Exception: If parameters cannot be retrieved or don't exist
        """
        # Check which parameters are already cached
        result = {}
        uncached_params = []
        
        for param_name in parameter_names:
            if param_name in self._cached_parameters:
                result[param_name] = self._cached_parameters[param_name]
            else:
                uncached_params.append(param_name)
        
        # If all parameters are cached, return immediately
        if not uncached_params:
            logger.info("All parameters found in cache")
            return result
        
        # Fetch uncached parameters in batch
        try:
            fetched_params = self._fetch_and_cache_parameters_batch(uncached_params, with_decryption)
            result.update(fetched_params)
            return result
        except Exception as e:
            # Retry once on failure
            logger.warning(f"Failed to fetch parameters batch, retrying: {str(e)}")
            try:
                fetched_params = self._fetch_and_cache_parameters_batch(uncached_params, with_decryption)
                result.update(fetched_params)
                return result
            except Exception as inner_e:
                error_message = f"Failed to fetch SSM parameters batch: {str(inner_e)}"
                logger.error(error_message)
                raise Exception(error_message)

    def trigger_refetch_api_key(self, parameter_name: str):
        """
        Force a refresh of the cached parameter
        
        Args:
            parameter_name: The name of the parameter to refresh
        """
        if parameter_name in self._cached_parameters:
            del self._cached_parameters[parameter_name]
            logger.info(f"Cleared cache for parameter {parameter_name}")

    def _fetch_and_cache_parameter(self, parameter_name: str, with_decryption: bool) -> str:
        """
        Fetch parameter from SSM and store in cache
        
        Args:
            parameter_name: The name of the parameter in SSM
            with_decryption: Whether to decrypt the parameter value
            
        Returns:
            The parameter value as a string
            
        Raises:
            Exception: If the parameter value is None or empty
        """
        response = self._ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=with_decryption
        )
        
        parameter_value = response.get('Parameter', {}).get('Value')
        if not parameter_value:
            error_message = f"API key not found in {parameter_name}"
            logger.error(error_message)
            raise Exception(error_message)
            
        # Cache the parameter
        self._cached_parameters[parameter_name] = parameter_value
        logger.info(f"Successfully fetched and cached parameter {parameter_name}")
        
        return parameter_value

    def _fetch_and_cache_parameters_batch(self, parameter_names: list[str], with_decryption: bool) -> Dict[str, str]:
        """
        Fetch multiple parameters from SSM in a single batch call and store in cache
        
        Args:
            parameter_names: List of parameter names in SSM
            with_decryption: Whether to decrypt the parameter values
            
        Returns:
            Dictionary mapping parameter names to their values
            
        Raises:
            Exception: If any parameter value is None, empty, or invalid
        """
        response = self._ssm_client.get_parameters(
            Names=parameter_names,
            WithDecryption=with_decryption
        )
        
        # Check for invalid parameters
        invalid_params = response.get('InvalidParameters', [])
        if invalid_params:
            error_message = f"Invalid SSM parameters: {', '.join(invalid_params)}"
            logger.error(error_message)
            raise Exception(error_message)
        
        # Process and cache all parameters
        result = {}
        parameters = response.get('Parameters', [])
        
        if len(parameters) != len(parameter_names):
            error_message = f"Expected {len(parameter_names)} parameters but got {len(parameters)}"
            logger.error(error_message)
            raise Exception(error_message)
        
        for param in parameters:
            param_name = param.get('Name')
            param_value = param.get('Value')
            
            if not param_value:
                error_message = f"API key not found or empty in {param_name}"
                logger.error(error_message)
                raise Exception(error_message)
            
            # Cache the parameter
            self._cached_parameters[param_name] = param_value
            result[param_name] = param_value
        
        logger.info(f"Successfully fetched and cached {len(parameters)} parameters in batch")
        
        return result
