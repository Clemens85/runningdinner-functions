import json

from langsmith import traceable
from SupportBot import SupportBot
from UserRequest import UserRequest
from UserResponse import UserResponse
from langchain_core.runnables import RunnableConfig

from Util import is_running_on_lambda
from VectorDbRepository import VectorDbRepository
from memory.MemoryProvider import MemoryProvider
from HttpUtil import APPLICATION_JSON
from logger.Log import Log
import langsmith as ls

class SupportRequestHandler:
    
    def __init__(self, memory_provider: MemoryProvider, vector_db_repository: VectorDbRepository):
        self.memory_provider = memory_provider
        self.vector_db_repository = vector_db_repository

    @traceable
    def process_user_request(self, user_request: UserRequest):
        self._add_tracing_metadata(user_request)

        configurable = self._new_configurable_from_user_request(user_request=user_request)
        support_bot = SupportBot(memory_provider=self.memory_provider, vector_db_repository=self.vector_db_repository, thread_id=user_request.thread_id)
        response = support_bot.query(user_request, configurable)

        user_response = UserResponse(answer=response, thread_id=user_request.thread_id)

        # Remove thread_id context after request is done
        Log.remove_keys(["thread_id"])
        return {
            "statusCode": 200,
            "headers": {"Content-Type": APPLICATION_JSON},
            "body": user_response.model_dump_json(indent=2)
        }

    def process_error(self, e: Exception):
        Log.exception(f"An error occurred while processing a request {str(e)}")
        # Remove thread_id context after request is done
        Log.remove_keys(["thread_id"])
        return {
            "statusCode": 500,
            "headers": {"Content-Type": APPLICATION_JSON},
            "body": json.dumps({"error": str(e)})
        }

    def _new_configurable_from_user_request(self, user_request: UserRequest) -> RunnableConfig:
        return {"configurable": {
            "thread_id": user_request.thread_id
        }}
    

    def warm_up(self):
        try: 
            Log.info("Warming up SupportBot and its workflow graph...")
            support_bot = SupportBot(memory_provider=self.memory_provider, vector_db_repository=self.vector_db_repository, thread_id="warmup-thread")
            support_bot.build_workflow_graph()
            Log.info("... warmed up SupportBot and its workflow graph")
            return {
                "statusCode": 200,
                "headers": {"Content-Type": APPLICATION_JSON}
            }
        except Exception as e:
            Log.exception("Exception during warm up: %s", str(e))
            return self.process_error(e)

    def _add_tracing_metadata(self, user_request: UserRequest):
        run_tree = ls.get_current_run_tree()
        stage = "prod" if is_running_on_lambda() else "local"
        if run_tree is not None:
            run_tree.metadata["thread_id"] = user_request.thread_id
            run_tree.metadata["stage"] = stage
            run_tree.tags.extend([stage])

        # Add thread_id to all subsequent logs
        Log.append_keys(thread_id=user_request.thread_id)