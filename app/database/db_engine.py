import os
from src.database.db_config import DB_URL, SCHEMA
from src.database.db_models import Base, PromptFeedback, PromptFeedbackValidator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# Create SQLAlchemy engine
engine = create_engine(DB_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Function to create the schema and tables
def create_schema_and_tables():
    # Create a connection
    with engine.connect() as connection:
        # Create schema
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))
        connection.commit()

    # Create tables
    Base.metadata.create_all(bind=engine)


# Function to insert validated data
def insert_validated_data(prompt: str, entities: dict, json_data: dict, feedback: bool):
    # Validate data using Pydantic model
    validated_data = PromptFeedbackValidator(
        prompt=prompt, entities=entities, json_data=json_data, feedback=feedback
    )

    # Create SQLAlchemy session
    db = SessionLocal()
    try:
        # Create new PromptFeedback instance
        new_entry = PromptFeedback(**validated_data.model_dump())
        db.add(new_entry)
        db.commit()
        print("Data inserted successfully")
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()
