import os
from typing import List

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from ..DocumentVectorizable import DocumentVectorizable
from ..VectorDbRepository import VectorDbRepository
from llm.ChatOpenAI import ChatOpenAI

os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY', '')
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_CLOUD = os.getenv('PINECONE_CLOUD', 'aws')
PINECONE_REGION = os.getenv('PINECONE_REGION', 'us-east-1') 

INDEX_NAME = "TODO" # TODO: set your index name here

EMBEDDING_MODEL = 'text-embedding-3-small'

class PineconeDbRepository(VectorDbRepository):

    def __init__(self, llm: ChatOpenAI, index_name: str = INDEX_NAME, auto_create: bool = False):
        self.llm = llm
        self.index_name = index_name
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.__init_index(auto_create=auto_create)
    
    def __init_index(self, auto_create: bool = False):
        """Initialize the Pinecone index or verify it exists"""
        # Check if the index already exists
        if not self.pc.has_index(self.index_name) and auto_create:
            # For free tier, we can only create in us-east-1 region
            print(f"Creating new Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI text-embedding-3-small dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=PINECONE_CLOUD,
                    region=PINECONE_REGION
                )
            )
        
        # Get the index
        self.index = self.pc.Index(self.index_name)

    def add_document(self, doc_id: str, document: DocumentVectorizable):
        """
        Add a document to the Pinecone index with its embedding
        
        Args:
            doc_id (str): The unique id
            document (Document): The document
        """
        
        # Create metadata with the document text
        metadata = {
            "text": document.page_content,
            "id": document.id,
            "proposal_type": document.type,
            "source_path": document.source_path,
            "admin_id": document.admin_id,
            **document.metadata
        }
        

        # Generate embedding for the document text
        text_embedding = self.__embed_text(document.page_content)

        # Upsert the document embedding to the Pinecone index
        self.index.upsert(
            vectors=[(doc_id, text_embedding, metadata)]
        )
    
    def __embed_text(self, text: str) -> list[float]:
        return  self.llm.embed_text(text=text, embedding_model=EMBEDDING_MODEL)

    def reset(self):
        """
        Reset the Pinecone index by deleting it and recreating it
        """
        print(f"Calling reset on Pinecone index {self.index_name}...")
        if self.pc.has_index(self.index_name):
            # Delete the existing index
            print(f"Resetting Pinecone index {self.index_name}...")
            self.pc.delete_index(self.index_name)
        
        # Recreate the index (ensure auto_create=True)
        print(f"Recreating Pinecone index {self.index_name}...")
        self.__init_index(auto_create=True)
      
    def find_similar_docs(self, query: str, top_k: int = 3) -> List[DocumentVectorizable]:
        """
        Find similar documents in the Pinecone index based on a query string
        
        Args:
            query (str): The query string to search for similar documents
            top_k (int): The number of top similar documents to return
        
        Returns:
            list[str]: List of document texts that are similar to the query
        """

        query_embedding = self.__embed_text(query)

        # Perform the query to find similar documents
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        return [
            DocumentVectorizable(
                page_content=match['metadata']['text'],
                id=match['metadata'].get('id'),
                type=match['metadata'].get('proposal_type'),
                source_path=match['metadata'].get('source_path'),
                admin_id=match['metadata'].get('admin_id'),
                metadata={k: v for k, v in match['metadata'].items() if k not in ['text', 'id', 'proposal_type', 'source_path', 'admin_id']}
            )
            for match in results['matches']
        ]
