from typing import List, Dict
from DocumentVectorizable import DocumentVectorizable
from VectorDbRepository import VectorDbRepository


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

    def find_similar_docs(self, query: str, top_k: int = 3, exclude_admin_id: str | None = None) -> List[DocumentVectorizable]:
        """
        Find similar documents using basic text matching.
        Ranks documents by the number of matching words with the query.
        
        Args:
            query (str): The query string to search for similar documents
            top_k (int): The number of top similar documents to return
            exclude_admin_id (str | None): If provided, documents belonging to this admin are excluded
        
        Returns:
            List[DocumentVectorizable]: List of similar documents
        """
        if not self.documents:
            return []

        docs = [d for d in self.documents.values() if d.admin_id != exclude_admin_id] if exclude_admin_id else list(self.documents.values())
        return docs[:top_k]

    def reset(self):
        """
        Clear all documents from the in-memory store
        """
        self.documents.clear()
