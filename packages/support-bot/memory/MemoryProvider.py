
from langgraph.checkpoint.memory import MemorySaver

class MemoryProvider:

    def __init__(self):
        self.memory_saver = MemorySaver()

    def get(self) -> MemorySaver:
        return self.memory_saver
        
