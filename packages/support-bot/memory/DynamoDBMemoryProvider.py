from langgraph_checkpoint_aws import DynamoDBSaver

# Table name uses v2 because langgraph-checkpoint-aws uses a different data
# format (ref_key/ref_loc structure) than the old langgraph-checkpoint-amazon-dynamodb
# package (which used a different serialization schema). The old supportbot-v1
# table data would cause KeyErrors when read by the new saver.
_TABLE_NAME = "supportbot-v2"
_REGION_NAME = "eu-central-1"
_TTL_SECONDS = 86400 * 5  # 5 days


class DynamoDBMemoryProvider:
    """Wraps the official langgraph-checkpoint-aws DynamoDBSaver.

    Unlike the old langgraph-checkpoint-amazon-dynamodb package, this saver:
    - Does NOT call describe_table() at init (no blocking network call at cold start)
    - Does NOT use aioboto3 (no async event-loop conflicts in sync Lambda handlers)
    - Async methods are implemented via run_in_executor (safe for sync callers)
    """

    def __init__(self):
        self.checkpointer = DynamoDBSaver(
            table_name=_TABLE_NAME,
            region_name=_REGION_NAME,
            ttl_seconds=_TTL_SECONDS,
        )

    def get_checkpointer(self) -> DynamoDBSaver:
        return self.checkpointer
