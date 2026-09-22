"""Pydantic schemas for ML predictions, datasets, and drift detection API contracts."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    features: dict[str, Any] = Field(..., description="Feature key-value pairs for model prediction")
    model_name: Optional[str] = Field(None, description="Optional target model name, defaults to active production model")
    model_version: Optional[str] = Field(None, description="Optional target model version")


class PredictResponse(BaseModel):
    prediction: Any = Field(..., description="Model prediction output (class label or numerical value)")
    probabilities: Optional[dict[str, float]] = Field(None, description="Class probabilities for classification models")
    model_name: str = Field(..., description="Model name used for inference")
    model_version: str = Field(..., description="Model version used for inference")
    execution_time_ms: float = Field(..., description="Inference execution time in milliseconds")


class DatasetIngestRequest(BaseModel):
    dataset_name: str = Field(..., description="Name of dataset")
    data_path: str = Field(..., description="File path to raw dataset CSV/Parquet")
    test_split_ratio: float = Field(0.2, ge=0.05, le=0.5, description="Ratio for test split")
    target_column: str = Field(..., description="Target column name")


class DriftCheckRequest(BaseModel):
    reference_data_path: str = Field(..., description="Path to reference baseline dataset")
    current_data_path: str = Field(..., description="Path to current dataset to check for drift")
    target_column: str = Field(..., description="Target column name")
    threshold: float = Field(0.05, description="Significance threshold for drift detection")


class DriftCheckResponse(BaseModel):
    drift_detected: bool = Field(..., description="True if overall dataset drift exceeds threshold")
    drift_share: float = Field(..., description="Share of drifted features between 0.0 and 1.0")
    drifted_features: list[str] = Field(default_factory=list, description="List of feature names with detected drift")
    report_html_path: Optional[str] = Field(None, description="Path to generated Evidently HTML report")
