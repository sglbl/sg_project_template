"""MLflow implementation of ITrackerRepository and IRegistryRepository."""

import os
from pathlib import Path
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
        self._active_run_id: Optional[str] = None

        # Configure environment for S3/RustFS/MinIO access if present
        endpoint = getattr(settings, "RUSTFS_ENDPOINT_URL", None) or settings.MINIO_ENDPOINT_URL
        if endpoint:
            os.environ["MLFLOW_S3_ENDPOINT_URL"] = endpoint
            os.environ["AWS_ACCESS_KEY_ID"] = settings.AWS_ACCESS_KEY_ID
            os.environ["AWS_SECRET_ACCESS_KEY"] = settings.AWS_SECRET_ACCESS_KEY
            os.environ["AWS_DEFAULT_REGION"] = settings.AWS_REGION

        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.experiment_name)
            self.client = MlflowClient(tracking_uri=self.tracking_uri)
            # Test connection
            self.client.search_experiments(max_results=1)
            logger.info(f"Connected MLflow tracker to {self.tracking_uri} [experiment: {self.experiment_name}]")
        except Exception as e:
            local_uri = "sqlite:///mlflow.db"
            logger.warning(f"Could not connect to MLflow server at {self.tracking_uri}: {e}. Falling back to local tracking at {local_uri}.")
            self.tracking_uri = local_uri
            mlflow.set_tracking_uri(local_uri)
            mlflow.set_experiment(self.experiment_name)
            self.client = MlflowClient(tracking_uri=local_uri)

    # --- ITrackerRepository Methods ---

    def start_run(
        self,
        run_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> str:
        """Start a new experiment tracking run and return run_id."""
        try:
            active_run = mlflow.start_run(run_name=run_name, tags=tags)
        except Exception as e:
            logger.warning(f"Failed starting run on {self.tracking_uri}: {e}. Retrying with local sqlite...")
            self.tracking_uri = "sqlite:///mlflow.db"
            mlflow.set_tracking_uri(self.tracking_uri)
            active_run = mlflow.start_run(run_name=run_name, tags=tags)

        run_id = str(active_run.info.run_id)
        self._active_run_id = run_id
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
        description: Optional[str] = None,
    ) -> str:
        """Register a model artifact in MLflow Model Registry."""
        try:
            # Ensure registered model container exists
            try:
                self.client.create_registered_model(name=model_name)
            except Exception:
                pass

            if self._active_run_id:
                uri = f"runs:/{self._active_run_id}/{Path(artifact_path).name}"
                result = self.client.create_model_version(
                    name=model_name,
                    source=uri,
                    run_id=self._active_run_id,
                    tags=tags,
                    description=description,
                )
            else:
                uri = artifact_path
                result = self.client.create_model_version(
                    name=model_name,
                    source=uri,
                    tags=tags,
                    description=description,
                )

            version = str(result.version)
            logger.info(f"Successfully registered model '{model_name}' version {version}")
            return version
        except Exception as e:
            logger.warning(f"Could not register model in MLflow: {e}. Generating local version tag.")
            return "1"

    def transition_stage(self, model_name: str, version: str, stage: ModelStage) -> None:
        """Transition model version stage in registry."""
        try:
            int_version = version.split(".")[0] if "." in version else version
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning)
                self.client.transition_model_version_stage(
                    name=model_name,
                    version=int_version,
                    stage=stage.value,
                    archive_existing_versions=(stage == ModelStage.PRODUCTION),
                )
            try:
                self.client.set_registered_model_alias(
                    name=model_name,
                    alias=stage.value.lower(),
                    version=int_version,
                )
            except Exception:
                pass
            logger.info(f"Transitioned model '{model_name}' v{int_version} to stage {stage.value}")
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
