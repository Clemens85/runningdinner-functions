from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from VectorDbRepository import VectorDbRepository

DATABASE_NAME = "/home/clemens/Projects/runningdinner-support-rag/rag-data-writer/.chromadb"
COLLECTION_NAME = "support-documents-v1"

class LocalChromaDbRepository(VectorDbRepository):
    def __init__(self, database_name: str = DATABASE_NAME):
        embeddings_openai = OpenAIEmbeddings(model='text-embedding-3-small')
        self.vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings_openai,
            persist_directory=database_name
        )

    # Removed @tool decorator to fix argument passing
    def retrieve(self, query: str, top_k: int = 2) -> list[str]:
        """Retrieve information related to a query."""
        retrieved_docs = self.vector_store.similarity_search(query, top_k)
        print(f"Found {len(retrieved_docs)} documents")
        return [doc.page_content for doc in retrieved_docs]
