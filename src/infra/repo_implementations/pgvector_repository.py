import os
from src.config import settings
from src.domain.repo_interfaces.vectordb_repository import IVectorDBRepository
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever


class PostgresVectorDBRepository(IVectorDBRepository):
    def __init__(self):
        self.create_document_store()
        self.create_embedding_retriever(top_k=25)
        
    def create_document_store(self, table_name: str = "embeddings", dim: int = 768):
        # create_embeddings_table(cursor, table_name="embeddings2", dim=3)
        print("Creating document store with pgvector...")

        os.environ["PG_CONN_STR"] = settings.SYNC_DB_URL

        self.document_store = PgvectorDocumentStore(
            schema_name=settings.DB_SCHEMA,
            table_name=table_name,
            recreate_table=True,
            vector_function="cosine_similarity",
            embedding_dimension=dim,
        )
        return self.document_store
    
    def create_embedding_retriever(self, top_k):
        self.embedding_retriever = PgvectorEmbeddingRetriever(document_store=self.document_store, top_k=top_k)
        return self.embedding_retriever
