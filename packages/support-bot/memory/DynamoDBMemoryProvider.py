from langgraph_checkpoint_dynamodb import DynamoDBConfig, DynamoDBTableConfig, DynamoDBSaver

class DynamoDBMemoryProvider:

    def __init__(self):
        config = DynamoDBConfig(
            table_config=DynamoDBTableConfig(
                table_name="supportbot-v1",
                ttl_attribute="expireAt",
                ttl_days=5,
                enable_point_in_time_recovery=False,
            ),
            region_name="eu-central-1"
        )
        self.checkpointer = DynamoDBSaver(config, deploy=False)

    def get_checkpointer(self) -> DynamoDBSaver:
        return self.checkpointer
