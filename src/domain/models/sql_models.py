# Domain models [data models as classes]
import json
import numpy as np
import pandas as pd
from enum import Enum
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, RootModel, ConfigDict, ValidationError, field_validator, create_model, validator
from sqlalchemy import ARRAY, Float, Column, Index
from sqlalchemy.dialects.postgresql import JSONB
from src.config import settings

# EVERY_SQL_MODEL_TO_CREATE_DECLARATIVELY

class DataGraph(SQLModel, table=True):
    __tablename__: str = "data_graph" #  type: ignore (pyright)
    __table__args__ = {'schema': settings.DB_SCHEMA}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    data_fk: str = Field(foreign_key="data.name")
    values: dict[str, float] = Field(sa_column=Column(JSONB))
    
    # Define the relationship back to Data
    data: "Data" = Relationship(back_populates="data_graphs")

    # Validator for values to ensure each timestamp has a single float value
    @field_validator("values")
    @classmethod
    def check_values_are_floats(cls, v):
        if not all(isinstance(value, (int, float)) for value in v.values()):
            raise ValueError("Each value in values must be a numeric value (float or int).")
        return v

    # Use model_validate to validate each instance when creating it from a dict
    @classmethod
    def from_dict(cls, data: dict) -> "DataGraph":
        return cls.model_validate(data)
    
    @classmethod
    def from_json(cls, path: str) -> list["DataGraph"]:
        # Read the JSON file
        with open(path, "r") as f:
            data = json.load(f)
        
        all_data_graph = []
        # Extract the records from the JSON data
        # data = data.get("all_data_graph", [])
        # Validate each row as a DataGraph
        for record in data:
            validated_row = cls.model_validate(record)
            all_data_graph.append(validated_row)
        return all_data_graph

        

class Data(SQLModel, table=True):
    __tablename__: str = "data"  #  type: ignore
    __table__args__ = {'schema': settings.DB_SCHEMA}

    name: Optional[str] = Field(default=None, primary_key=True, index=False, nullable=True)
    graphs: list["DataGraph"] = Relationship(back_populates="data", sa_relationship_kwargs={"lazy": "joined"})
    