from typing import Protocol


class IVectorDBRepository(Protocol):
    def create_document_store(self):
        ...
    def create_embedding_retriever(self, document_store, top_k):
        ...
