# from src.domain.models.data_models import *
from src.domain.repo_interfaces.vectordb_repository import IVectorDBRepository
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever


class QdrantDBRepository(IVectorDBRepository):
    def __init__(self):
        self.create_document_store()
        self.create_embedding_retriever(top_k=25)
        
    def create_document_store(self):
        self.document_store = QdrantDocumentStore(
            ":memory:",
            # path="./data/qdrant_data",
            recreate_index=True,
            return_embedding=True,
            wait_result_from_api=True
        )   
        return self.document_store
    
    def create_embedding_retriever(self, top_k):
        self.embedding_retriever = QdrantEmbeddingRetriever(document_store=self.document_store, top_k=top_k)
        return self.embedding_retriever
