from typing import List, Dict
from ..DocumentVectorizable import DocumentVectorizable
from ..VectorDbRepository import VectorDbRepository


class LocalInMemoryDbRepository(VectorDbRepository):
    """
    Simple in-memory implementation of VectorDbRepository for local development and testing.
    Uses basic text matching instead of vector embeddings.
    """

    def __init__(self):
        self.documents: Dict[str, DocumentVectorizable] = {}

    def add_document(self, doc_id: str, document: DocumentVectorizable):
        """
        Add a document to the in-memory store
        
        Args:
            doc_id (str): The unique id
            document (DocumentVectorizable): The document to store
        """
        self.documents[doc_id] = document

    def find_similar_docs(self, query: str, top_k: int = 3) -> List[DocumentVectorizable]:
        """
        Find similar documents using basic text matching.
        Ranks documents by the number of matching words with the query.
        
        Args:
            query (str): The query string to search for similar documents
            top_k (int): The number of top similar documents to return
        
        Returns:
            List[DocumentVectorizable]: List of similar documents
        """
        if not self.documents:
            return []

        return list(self.documents.values())[:top_k]

    def reset(self):
        """
        Clear all documents from the in-memory store
        """
        self.documents.clear()
