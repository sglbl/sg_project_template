"""Domain interface protocol for Model Registry."""

from typing import Optional, Protocol
from src.domain.models.ml_entities import ModelMetadata, ModelStage


class IRegistryRepository(Protocol):
    def register_model(
        self,
        model_name: str,
        artifact_path: str,
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        """Register a new model artifact and return registered version string."""
        ...

    def transition_stage(self, model_name: str, version: str, stage: ModelStage) -> None:
        """Promote or transition a model version to a target stage (Development, Staging, Production, Archived)."""
        ...

    def get_latest_model(self, model_name: str, stage: ModelStage = ModelStage.PRODUCTION) -> ModelMetadata:
        """Fetch metadata for the latest model version in a given stage."""
        ...
