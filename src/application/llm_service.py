import os
import dotenv
import time
from loguru import logger
from overrides import override
from src.domain.models.data_models import *
from src.application.service_interfaces.llm_abstraction import ILLMService
from src.domain.repo_interfaces.vectordb_repository import IVectorDBRepository

from haystack import Pipeline
from haystack_integrations.components.generators.ollama import OllamaGenerator
from haystack.components.writers import DocumentWriter
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.converters import PyPDFToDocument, CSVToDocument


class LLMService(ILLMService):
    """LLM Pipeline service

    Superclass:
        ILLMService (Interface): Interface for the LLM Pipeline
    """
    
    def __init__(self, vectordb_repository: IVectorDBRepository):
        self.vectordb_repository = vectordb_repository

    @override
    def create_model(self, llm_model_name, embedding_model_name, mode=Modes.OLLAMA):
        logger.opt(colors=True).info(f"\nUsing the LLM Model <bg #AF5FD7>'{llm_model_name}'</>") # and {embedding_model_name}")    
        if mode == Modes.OPENAI:
            dotenv.load_dotenv(override=True)
            openai_token = os.getenv("OPENAI_API_KEY")
            self.llmmodel = LLMModel(name=llm_model_name, url="NOT_USED", embedding_name=embedding_model_name, embedding_dim=1536, mode=mode, api_key=openai_token)
        else: # Modes.OLLAMA
            self.llmmodel = LLMModel(name=llm_model_name, url="https://ollama-plain.deducedata.solutions/api/generate", embedding_name=embedding_model_name)

        self.create_pipelines()


    @override
    def create_pipelines(self):    
        document_store = self.vectordb_repository.create_document_store()
        # PIPELINE CSV
        self.pipeline_csv = self.create_indexing_pipeline(document_store, converter=CSVToDocument(encoding="unicode_escape"), metadata_fields_to_embed=['file_name'])
        
        # MAIN RETRIEVAL PIPELINE
        self.retrieval_pipeline = self.create_retrieval_pipeline(document_store)
       

    @override
    def create_pipelines(self):    
        document_store = self.vectordb_repository.create_document_store()
        # PIPELINE PDF
        self.pipeline_pdf = self.create_indexing_pipeline(document_store, converter=PyPDFToDocument(), metadata_fields_to_embed=['file_name'])
        # MAIN RETRIEVAL PIPELINE
        self.retrieval_pipeline = self.create_retrieval_pipeline(document_store)
                

    @override
    def create_indexing_pipeline(self, document_store, converter, metadata_fields_to_embed=None):
        # PIPELINE TXT or PDF
        pipeline_indexing = Pipeline()
        pipeline_indexing.add_component("converter", converter)
        pipeline_indexing.add_component("cleaner", DocumentCleaner())
        pipeline_indexing.add_component("splitter", DocumentSplitter(split_by="word", split_length=200, split_overlap = 30))
        pipeline_indexing.add_component("embedder", SentenceTransformersDocumentEmbedder(model=self.llmmodel.embedding_name, meta_fields_to_embed=metadata_fields_to_embed))
        pipeline_indexing.add_component("writer", DocumentWriter(document_store=document_store, policy=DuplicatePolicy.OVERWRITE))
        
        pipeline_indexing.connect("converter", "cleaner")
        pipeline_indexing.connect("cleaner", "splitter")
        pipeline_indexing.connect("splitter", "embedder")
        pipeline_indexing.connect("embedder", "writer")
        
        return pipeline_indexing


    @override
    def create_retrieval_pipeline(self, document_store):
        template = """
        Given only the following information, answer the question.
        Ignore your own knowledge.

        Context:
        {% for document in documents %}
            {{ document.content }}
        {% endfor %}

        Question: {{ query }}?
        """

        retrieval_pipeline = Pipeline()
        retrieval_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder(model=self.llmmodel.embedding_name))
        retrieval_pipeline.add_component("retriever", QdrantEmbeddingRetriever(document_store=document_store, top_k=20))
        retrieval_pipeline.add_component("prompt_builder", PromptBuilder(template=template))
        retrieval_pipeline.add_component("llm", OllamaGenerator(model=self.llmmodel.name, timeout=250, url=self.llmmodel.url))
        retrieval_pipeline.add_component(name="answer_builder", instance=AnswerBuilder())

        retrieval_pipeline.connect("text_embedder", "retriever")    
        retrieval_pipeline.connect("retriever", "prompt_builder")
        retrieval_pipeline.connect("prompt_builder", "llm")
        retrieval_pipeline.connect("llm.replies", "answer_builder.replies")
        retrieval_pipeline.connect("llm.meta", "answer_builder.meta")
        retrieval_pipeline.connect("retriever", "answer_builder.documents")

        return retrieval_pipeline


    @override
    def llm_rag_handler(self, query, query_files):
        """Main function to handle query and generate responses"""

        print(f'Running indexing pipeline')
        source_file_path = query_files[0] if query_files else "No file provided"

        pdf_query_files = [file for file in query_files if file.endswith(".pdf")]
        if pdf_query_files:
            self.pipeline_pdf.run({"converter": {"sources": pdf_query_files, "meta": {"file_name": source_file_path}}})    
        

        response = self.retrieval_pipeline.run({
            "text_embedder": {"text": query},
            "prompt_builder": {"query": query}, 
            "answer_builder": {"query": query},
                }, 
                include_outputs_from={"prompt_builder"})

        prompt = response["prompt_builder"]["prompt"]
        print(f"""LLM Reply: {response["answer_builder"]["answers"][0].data}""")
        return response["answer_builder"]["answers"][0].data, prompt

    @override
    def ask_rag_pipeline(self, chat_input):
        model_result = f"RAG: {chat_input}"
        for i in range(len(model_result)):
            time.sleep(0.0001)
            yield model_result[: i+1], None
            
        yield model_result, {"metadata": "metadata"}
        return model_result, {"metadata": "metadata"}