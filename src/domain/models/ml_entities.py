"""Domain entities and data classes for MLOps datasets, models, and evaluation."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ModelStage(Enum):
    DEVELOPMENT = "Development"
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"


@dataclass
class DatasetMetadata:
    name: str
    version: str
    num_rows: int
    num_features: int
    feature_names: list[str]
    split_ratio: float = 0.2
    checksum: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ModelMetadata:
    name: str
    version: str
    stage: ModelStage = ModelStage.DEVELOPMENT
    metrics: dict[str, float] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    artifact_path: Optional[str] = None
    framework: str = "scikit-learn"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class EvaluationReport:
    model_name: str
    model_version: str
    metrics: dict[str, float]
    drift_detected: bool
    drift_share: float
    report_path: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
