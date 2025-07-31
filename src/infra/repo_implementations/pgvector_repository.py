import os
from src.config import settings
from src.domain.repo_interfaces.vectordb_repository import IVectorDBRepository
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever
from src.infra.postgres.create_vdb import connect_to_db, setup_schema, create_embeddings_table


class PostgresVectorDBRepository(IVectorDBRepository):
    def __init__(self):
        self.create_document_store()
        self.create_embedding_retriever(top_k=25)
        
    def create_document_store(self):
        conn = connect_to_db()
        cursor = conn.cursor()
        setup_schema(cursor, schema_name=settings.DB_SCHEMA)
        # create_embeddings_table(cursor, table_name="embeddings2", dim=3)
        print("Creating document store with pgvector...")
        # os.environ["PG_CONN_STR"] = settings.DB_URL
        os.environ["PG_CONN_STR"] = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

        self.document_store = PgvectorDocumentStore(
            schema_name=settings.DB_SCHEMA,
            table_name="embeddings2",
            recreate_table=True,
            vector_function="cosine_similarity",
            embedding_dimension=768,
        )
        return self.document_store
    
    def create_embedding_retriever(self, top_k):
        self.embedding_retriever = PgvectorEmbeddingRetriever(document_store=self.document_store, top_k=top_k)
        return self.embedding_retriever
