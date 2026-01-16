from asyncio import sleep
from agents import set_trace_processors
from langsmith.wrappers import OpenAIAgentsTracingProcessor
from aws_lambda_powertools import Tracer, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext
from urllib.parse import unquote_plus
from aws_adapter.S3DataAccessor import S3DataAccessor
from ProposalInputHandler import ProposalInputHandler
from Environment import setup_environment
from aws_adapter.SNSNotificationHandler import SNSNotificationHandler
from logger.Log import logger
from pinecone.PineconeDbRepository import PineconeDbRepository
from llm.ChatOpenAI import ChatOpenAI
import langsmith as ls

tracer = Tracer()
metrics = Metrics(namespace="runningdinner-functions", service="message-proposal")

set_trace_processors([OpenAIAgentsTracingProcessor()])
setup_environment()

@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, _context: LambdaContext):
    logger.info("Processing event: %s", event)
    _add_tracing_metadata()

    for record in event.get("Records", []):
        s3_info = record["s3"]
        source_bucket = s3_info["bucket"]["name"]
        source_key = unquote_plus(s3_info["object"]["key"])

        logger.info(f"Processing file: s3://{source_bucket}/{source_key}")

        logger.append_keys(source_key=source_key)

        try:
            process_single_request(source_bucket, source_key)
            sleep(1)  # To give langsmith some time to flush traces
        except Exception as e:
            logger.exception("Unhandled exception when processing %s", source_key)
            raise e

def _add_tracing_metadata():
    run_tree = ls.get_current_run_tree()
    stage = "prod"
    if run_tree is not None:
        run_tree.metadata["service"] = "message-proposal"
        run_tree.metadata["stage"] = stage
        run_tree.tags.extend([stage, "message-proposal"])

def process_single_request(source_bucket: str, source_key: str):
    data_accessor = S3DataAccessor(source_bucket)
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.3)
    vector_db_repository = PineconeDbRepository(llm=llm)
    notification_handler = SNSNotificationHandler()
    proposal_input_handler = ProposalInputHandler(data_accessor=data_accessor, vector_db_repository=vector_db_repository, llm=llm, notification_handler=notification_handler)
    proposal_input_handler.process_request(source_key)

