from typing import Protocol
from overrides import override
from src.domain.models.data_models import *
from src.application.utils import Interface
from src.domain.repo_interfaces.vectordb_repository import IVectorDBRepository


class ILLMService(Interface):    
    """LLM Pipeline interface

    Attributes:
    Protocol : Does not allow to create instances of the abstract class
    """
    def __init__(self, vectordb_repository: IVectorDBRepository):
        """LLM Pipeline service constructor

        Args:
            vectordb_repository (IVectorDBRepository): Repository for the vector database (qdrant, chroma, etc.)
        """
        raise NotImplementedError
    
    
    def create_model(self, llm_model_name: str, embedding_model_name: str, mode: Modes):
        """ Create the LLM, embedding model and pipelines

        Args:
            llm_model_name (str): LLM model name
            embedding_model_name (str): Embedding model name
            mode (Modes): Mode of the model (OpenAI or OLLAMA)
        """
        raise NotImplementedError
    

    def create_pipelines(self):
        """ Create the pipelines for the LLM model

        Raises
        ------
        NotImplementedError
            If the method is not implemented in the subclass
        """
        raise NotImplementedError


    def create_indexing_pipeline(self, document_store, converter, metadata_fields_to_embed: list[str]):
        """ Create the indexing pipeline that will be used to index the documents that has cleaner, splitter, and embedding

        Args:
            document_store: Qdrant, Chroma, etc.
            converter: CSVToDocument, PDFToDocument, etc.
            metadata_fields_to_embed (list[str]): Metadata fields (file_name, etc.)
            pipeline_proposal (bool): Is is a proposal pipeline?

        Returns:
            Pipeline: The indexing pipeline
        """
        raise NotImplementedError


    def create_retrieval_pipeline(self, document_store):
        """ Create the retrieval pipeline that will be used to retrieve the documents
            
        Args:
            document_store: Qdrant, Chroma, etc.
        """
        raise NotImplementedError


    def llm_rag_handler(self, query: str, query_files: list[str]):
        """ Main function to handle query and generate responses. Runs the pipeline for the LLM model 

        Args:
            query (str): The user question
            query_files (list[str]): Paths to the files

        Returns:
            Model answer, metadata as a dict, metadata as html, prompt
        """
        raise NotImplementedError

    def ask_rag_pipeline(chat_input: dict):
        return f"RAG: {chat_input}", f"Metadata"