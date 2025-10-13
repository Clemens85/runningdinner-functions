from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from Configuration import Configuration
from logger.Log import Log
from memory.DynamoDBMemoryProvider import DynamoDBMemoryProvider

class MemoryProvider:
    def __init__(self):
        config = Configuration.from_runnable_config()
        if config.use_checkpointer_in_memory:
            Log.info("Using InMemory-Saver as memory provider")
            self.memory_saver = MemorySaver()
        else:
            Log.info("Using DynamoDBMemoryProvider as memory provider")
            provider = DynamoDBMemoryProvider()
            self.memory_saver = provider.get_checkpointer()

    def get(self) -> BaseCheckpointSaver:
        return self.memory_saver
        
