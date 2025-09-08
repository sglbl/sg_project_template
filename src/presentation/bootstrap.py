# src/presentation/bootstrap.py
from src.infra.repo_implementations.qdrant_repository import QdrantDBRepository
from src.infra.repo_implementations.pgvector_repository import PostgresVectorDBRepository
from src.presentation.dependencies import get_llm_service

def create_services(model: str = "postgres") -> dict:
    """
    Initialize all application services and inject concrete adapters.
    
    model: str - choose which vectordb repository to use ('postgres' or 'qdrant')
    """
    if model.lower() == "qdrant":
        vectordb = QdrantDBRepository()
    else:
        vectordb = PostgresVectorDBRepository()

    llm_service = get_llm_service(vectordb)

    return {"llm_service": llm_service, "vectordb": vectordb}
