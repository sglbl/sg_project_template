from typing import Any, Protocol


class IVectorDBRepository(Protocol):
    def create_document_store(self) -> Any:
        ...
    def create_embedding_retriever(self, top_k: int) -> Any:
        ...
