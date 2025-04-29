# Domain models [data models as classes]
from enum import Enum
from dataclasses import dataclass


class Modes(Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"

@dataclass
class LLMModel:
    name: str
    url: str
    embedding_name: str
    embedding_dim: int = 768
    mode: Modes = Modes.OLLAMA
    api_key: str = None # only for OpenAI
    