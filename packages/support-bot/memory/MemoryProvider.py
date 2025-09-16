
from langgraph.checkpoint.memory import MemorySaver

class MemoryProvider:

    def get(self) -> MemorySaver:
        return MemorySaver()
        
