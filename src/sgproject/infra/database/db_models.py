from sgproject.infra.database.db_config import SCHEMA
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, JSON
from pydantic import BaseModel, field_validator

# Create a base class for declarative models
Base = declarative_base()


# Define a Table schema
class PromptFeedback(Base):
    __tablename__ = "prompt_feedback"
    __table_args__ = {"schema": SCHEMA}  # Use the SCHEMA variable here

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, index=True)
    entities = Column(JSON)
    json_data = Column(JSON)
    feedback = Column(Boolean)


# Define a Pydantic model for validation
class PromptFeedbackValidator(BaseModel):
    prompt: str
    entities: dict
    json_data: dict
    feedback: bool

    @field_validator("prompt")
    @classmethod
    def prompt_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Prompt must not be empty")
        return v

    @field_validator("json_data")
    @classmethod
    def json_data_must_not_be_empty(cls, v: dict) -> dict:
        if not v:
            raise ValueError("JSON data must not be empty")
        return v
