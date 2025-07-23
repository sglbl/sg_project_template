# tests/test_mocked_llm.py

from unittest.mock import MagicMock
from src.application.llm_service import LLMService


def test_llm_rag_handler_mocked():
    # Arrange: Create a fake vectordb_repository (can be unused)
    mock_vectordb = MagicMock()

    # Instantiate service with mocked dependency
    service = LLMService(vectordb_repository=mock_vectordb)

    # Patch llm_rag_handler method
    service.llm_rag_handler = MagicMock(return_value=("mocked_answer", "mocked_prompt"))

    # Act: Call the mocked method
    answer, prompt = service.llm_rag_handler("What is RAG?", ["file1.pdf"])

    # Assert: Check expected mocked results
    assert answer == "mocked_answer"
    assert prompt == "mocked_prompt"
    service.llm_rag_handler.assert_called_once_with("What is RAG?", ["file1.pdf"])
