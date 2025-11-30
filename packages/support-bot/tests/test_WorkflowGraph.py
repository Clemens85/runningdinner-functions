import os
from pathlib import Path
from typing import List

from SupportBot import SupportBot
from SupportDocument import SupportDocument
from VectorDbRepository import VectorDbRepository
from memory.MemoryProvider import MemoryProvider

os.environ["USE_CHECKPOINTER_IN_MEMORY"] = "True"
os.environ["LANGSMITH_TRACING"] = "False"
os.environ["GEMINI_ENABLED"] = "True"
os.environ["OPENAI_ENABLED"] = "False"
os.environ["GOOGLE_API_KEY"] = "Test"

class DummyVectorDbRepository(VectorDbRepository):
    def retrieve(self, query: str, top_k=2) -> List[SupportDocument]:
        pass

def test_build_draw_workflow_graph():
    support_bot = SupportBot(thread_id="123", memory_provider=MemoryProvider(), vector_db_repository=DummyVectorDbRepository())
    graph = support_bot.build_workflow_graph()
    parent_path = Path(__file__).parent
    graph.get_graph().draw_mermaid_png(output_file_path=parent_path / "graph.png")