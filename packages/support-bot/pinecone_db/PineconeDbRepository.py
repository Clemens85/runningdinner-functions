import os
from typing import List

from dotenv import load_dotenv
from pinecone import Pinecone

from SupportDocument import SupportDocument
from VectorDbRepository import VectorDbRepository
import openai

INDEX_NAME = "support-documents-v1"
EMBEDDING_MODEL = 'text-embedding-3-small'

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_CLOUD = os.getenv('PINECONE_CLOUD', 'aws')
PINECONE_REGION = os.getenv('PINECONE_REGION', 'us-east-1') 

class PineconeDbRepository(VectorDbRepository):
    
    def __init__(self, index_name: str = INDEX_NAME):
        self.index_name = index_name
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self._init_index()
        self.openai_api = openai.OpenAI()
    
    def _init_index(self):
        """Initialize the Pinecone index or verify it exists"""
        # Get the index
        self.index = self.pc.Index(self.index_name)

    def embed_text(self, text: str) -> list[float]:
        response = self.openai_api.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        embedding = response.data[0].embedding
        return embedding
    

    def retrieve(self, query: str, top_k: int = 3) -> List[SupportDocument]:
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

        return [
            SupportDocument(
                content=match['metadata']['text'],
                date=match['metadata'].get('date'),
                support_type=match['metadata'].get('support_type')
            )
            for match in results['matches']
        ]
