from typing import Protocol


class ILLMPipeline(Protocol):    
    def __init__(self, vectordb_repository):
        raise NotImplementedError
    
    def create_pipelines(self):    
        raise NotImplementedError     

    def create_indexing_pipeline(self, document_store, converter, llmmodel, metadata_fields_to_embed=None):
        raise NotImplementedError

    def create_retrieval_pipeline(self, document_store, llmmodel):
        raise NotImplementedError

    def llm_rag_handler(self, query, query_files):
        raise NotImplementedError
