import os
from dotenv import load_dotenv
from pinecone import Pinecone
from VectorDbRepository import VectorDbRepository
import openai

INDEX_NAME = "support-documents-v1"

load_dotenv(override=True)
os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY', '')
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_CLOUD = os.getenv('PINECONE_CLOUD', 'aws')
PINECONE_REGION = os.getenv('PINECONE_REGION', 'us-east-1') 

openai = openai.OpenAI()
EMBEDDING_MODEL = 'text-embedding-3-small'

class PineconeDbRepository(VectorDbRepository):
    
    def __init__(self, index_name: str = INDEX_NAME):
        self.index_name = index_name
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self._init_index()
    
    def _init_index(self):
        """Initialize the Pinecone index or verify it exists"""
        # Get the index
        self.index = self.pc.Index(self.index_name)

    def embed_text(self, text: str) -> list[float]:
        response = openai.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        embedding = response.data[0].embedding
        return embedding
    

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        """
        Find similar documents in the Pinecone index based on a query string
        
        Args:
            query (str): The query string to search for similar documents
            top_k (int): The number of top similar documents to return
        
        Returns:
            list[str]: List of document texts that are similar to the query
        """

        query_embedding = self.embed_text(query)

        # Perform the query to find similar documents
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Extract and return the document texts from the results
        similar_texts = [match['metadata']['text'] for match in results['matches']]
        return similar_texts

