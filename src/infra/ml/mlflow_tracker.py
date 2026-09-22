"""MLflow implementation of ITrackerRepository and IRegistryRepository."""

import os
from typing import Any, Optional
from loguru import logger
import mlflow
from mlflow.tracking import MlflowClient

from src.config import settings
from src.domain.models.ml_entities import ModelMetadata, ModelStage
from src.domain.repo_interfaces.tracker_repository import ITrackerRepository
from src.domain.repo_interfaces.registry_repository import IRegistryRepository


class MLflowTracker(ITrackerRepository, IRegistryRepository):
    """Experiment tracker and model registry backed by MLflow."""

    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        experiment_name: Optional[str] = None,
    ) -> None:
        self.tracking_uri = tracking_uri or settings.MLFLOW_TRACKING_URI
        self.experiment_name = experiment_name or settings.MLFLOW_EXPERIMENT_NAME

        # Configure environment for S3/RustFS/MinIO access if present
        if settings.MINIO_ENDPOINT_URL:
            os.environ["MLFLOW_S3_ENDPOINT_URL"] = settings.MINIO_ENDPOINT_URL
            os.environ["AWS_ACCESS_KEY_ID"] = settings.AWS_ACCESS_KEY_ID
            os.environ["AWS_SECRET_ACCESS_KEY"] = settings.AWS_SECRET_ACCESS_KEY
            os.environ["AWS_DEFAULT_REGION"] = settings.AWS_REGION

        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.experiment_name)
            self.client = MlflowClient(tracking_uri=self.tracking_uri)
            logger.info(f"Connected MLflow tracker to {self.tracking_uri} [experiment: {self.experiment_name}]")
        except Exception as e:
            logger.warning(f"Could not connect to MLflow server at {self.tracking_uri}: {e}. Falling back to local tracking.")
            self.client = MlflowClient()

    # --- ITrackerRepository Methods ---

    def start_run(self, run_name: Optional[str] = None) -> str:
        """Start a new experiment tracking run and return run_id."""
        active_run = mlflow.start_run(run_name=run_name)
        run_id = str(active_run.info.run_id)
        logger.info(f"Started MLflow run '{run_name or 'unnamed'}' (ID: {run_id})")
        return run_id

    def log_params(self, params: dict[str, Any]) -> None:
        """Log hyperparameter dictionary to active run."""
        try:
            mlflow.log_params(params)
        except Exception as e:
            logger.warning(f"Failed to log params to MLflow: {e}")

    def log_metrics(self, metrics: dict[str, float], step: Optional[int] = None) -> None:
        """Log evaluation metrics to active run."""
        try:
            mlflow.log_metrics(metrics, step=step)
        except Exception as e:
            logger.warning(f"Failed to log metrics to MLflow: {e}")

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """Log local file artifact to active run."""
        try:
            if os.path.exists(local_path):
                mlflow.log_artifact(local_path, artifact_path=artifact_path)
                logger.debug(f"Logged artifact {local_path} to MLflow")
            else:
                logger.warning(f"Artifact path not found: {local_path}")
        except Exception as e:
            logger.warning(f"Failed to log artifact {local_path} to MLflow: {e}")

    def end_run(self) -> None:
        """End the currently active experiment run."""
        try:
            mlflow.end_run()
            logger.info("Ended active MLflow run")
        except Exception as e:
            logger.warning(f"Failed to end active MLflow run: {e}")

    # --- IRegistryRepository Methods ---

    def register_model(
        self,
        model_name: str,
        artifact_path: str,
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        """Register a model artifact in MLflow Model Registry."""
        try:
            result = mlflow.register_model(model_uri=artifact_path, name=model_name, tags=tags)
            version = str(result.version)
            logger.info(f"Successfully registered model '{model_name}' version {version}")
            return version
        except Exception as e:
            logger.warning(f"Could not register model in MLflow: {e}. Generating local version tag.")
            return "1.0.0"

    def transition_stage(self, model_name: str, version: str, stage: ModelStage) -> None:
        """Transition model version stage in registry."""
        try:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage.value,
                archive_existing_versions=(stage == ModelStage.PRODUCTION),
            )
            logger.info(f"Transitioned model '{model_name}' v{version} to stage {stage.value}")
        except Exception as e:
            logger.warning(f"Could not transition model stage in MLflow: {e}")

    def get_latest_model(self, model_name: str, stage: ModelStage = ModelStage.PRODUCTION) -> ModelMetadata:
        """Fetch metadata for latest model in stage."""
        try:
            latest_versions = self.client.get_latest_versions(name=model_name, stages=[stage.value])
            if latest_versions:
                v = latest_versions[0]
                return ModelMetadata(
                    name=model_name,
                    version=str(v.version),
                    stage=stage,
                    artifact_path=v.source,
                    tags={k: str(val) for k, val in (v.tags or {}).items()},
                )
        except Exception as e:
            logger.warning(f"Could not fetch model '{model_name}' from MLflow registry: {e}")

        # Fallback local metadata
        return ModelMetadata(
            name=model_name,
            version="1.0.0",
            stage=stage,
            artifact_path=f"{settings.MODEL_ARTIFACTS_DIR}/{model_name}.onnx",
        )
