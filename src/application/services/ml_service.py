"""High-level ML orchestration service coordinating ingestion, training, export, and evaluation."""

from typing import Optional, Tuple
from loguru import logger

from src.application.pipelines.ingest import DataIngestionPipeline
from src.application.pipelines.train import ModelTrainingPipeline
from src.application.pipelines.export import ModelExportPipeline
from src.application.pipelines.evaluate import ModelEvaluationPipeline
from src.domain.models.ml_entities import DatasetMetadata, ModelMetadata, ModelStage
from src.domain.repo_interfaces.tracker_repository import ITrackerRepository
from src.domain.repo_interfaces.registry_repository import IRegistryRepository


class MLService:
    """End-to-end MLOps service orchestrating the full machine learning lifecycle."""

    def __init__(
        self,
        tracker: Optional[ITrackerRepository] = None,
        registry: Optional[IRegistryRepository] = None,
    ) -> None:
        self.tracker = tracker
        self.registry = registry
        self.ingest_pipe = DataIngestionPipeline()
        self.train_pipe = ModelTrainingPipeline(tracker=tracker)
        self.export_pipe = ModelExportPipeline()
        self.eval_pipe = ModelEvaluationPipeline()

    def run_ingest(self, file_path: str, target_col: str, dataset_name: str = "dataset") -> Tuple[str, str, DatasetMetadata]:
        """Load data, validate schema, split into train/test datasets."""
        logger.info(f"Ingesting dataset from {file_path}...")
        df = self.ingest_pipe.load_data(file_path)
        self.ingest_pipe.validate_schema(df, target_col=target_col)
        return self.ingest_pipe.split_and_save(df, target_col=target_col, dataset_name=dataset_name)

    def run_training(
        self,
        train_path: str,
        test_path: str,
        target_col: str,
        model_name: str = "model",
        tune: bool = False,
        export_onnx: bool = True,
    ) -> Tuple[str, Optional[str], ModelMetadata]:
        """Execute model training, tuning, artifact saving, and ONNX export."""
        logger.info(f"Starting training run for model '{model_name}'...")
        pkl_path, metadata = self.train_pipe.train_and_evaluate(
            train_path=train_path,
            test_path=test_path,
            target_col=target_col,
            model_name=model_name,
            tune=tune,
            close_run=False,
        )

        onnx_path: Optional[str] = None
        if export_onnx:
            try:
                onnx_path = self.export_pipe.export_to_onnx(pkl_path)
                metadata.artifact_path = onnx_path
            except Exception as e:
                logger.warning(f"Could not convert model to ONNX: {e}. Keeping .pkl artifact.")

        # Log ONNX artifact to active run if available
        if self.tracker and onnx_path:
            self.tracker.log_artifact(onnx_path)

        # Optional Model Registration
        if self.registry:
            tuning_desc = (
                f"Optuna tuned (trials: 10, accuracy: {metadata.metrics.get('accuracy', 0.0):.4f})"
                if tune
                else f"Untuned baseline (accuracy: {metadata.metrics.get('accuracy', 0.0):.4f})"
            )
            registry_tags = {
                "tuning": "optuna" if tune else "baseline",
                "accuracy": f"{metadata.metrics.get('accuracy', 0.0):.4f}",
                "precision": f"{metadata.metrics.get('precision', 0.0):.4f}",
                "f1_score": f"{metadata.metrics.get('f1_score', 0.0):.4f}",
            }
            version = self.registry.register_model(
                model_name=model_name,
                artifact_path=onnx_path or pkl_path,
                tags=registry_tags,
                description=tuning_desc,
            )
            self.registry.transition_stage(model_name, version, ModelStage.STAGING)
            metadata.version = version
            metadata.stage = ModelStage.STAGING

        # End active tracking run
        if self.tracker:
            self.tracker.end_run()

        # Publish artifact to RustFS / S3 storage
        try:
            import json
            import tempfile
            from pathlib import Path
            from src.infra.ml.storage import S3StorageProvider
            storage = S3StorageProvider()
            upload_target = onnx_path or pkl_path
            remote_key = f"models/{model_name}/{metadata.version}/{Path(upload_target).name}"
            dest_url = storage.upload_file(upload_target, remote_key)
            logger.info(f"Published model artifact to RustFS at {dest_url}")

            # Also publish companion metadata.json to RustFS for complete auditability
            meta_payload = {
                "model_name": model_name,
                "version": metadata.version,
                "tuning": "optuna" if tune else "baseline",
                "optimizer": "optuna" if tune else "default",
                "stage": metadata.stage.value if metadata.stage else "Staging",
                "framework": metadata.framework or "scikit-learn",
                "metrics": metadata.metrics,
                "parameters": metadata.parameters,
            }
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp_meta:
                json.dump(meta_payload, tmp_meta, indent=2)
                tmp_meta_path = tmp_meta.name
            remote_meta_key = f"models/{model_name}/{metadata.version}/metadata.json"
            storage.upload_file(tmp_meta_path, remote_meta_key)
            Path(tmp_meta_path).unlink(missing_ok=True)
            logger.info(f"Published model metadata to RustFS at s3://{storage.bucket_name}/{remote_meta_key}")
        except Exception as e:
            logger.warning(f"Could not publish model artifact to RustFS: {e}")

        return pkl_path, onnx_path, metadata

    def run_drift_check(
        self,
        reference_data_path: str,
        current_data_path: str,
        report_name: str = "data_drift_report",
    ) -> Tuple[bool, float, str]:
        """Run data drift detection using Evidently."""
        return self.eval_pipe.run_drift_analysis(
            reference_data_path=reference_data_path,
            current_data_path=current_data_path,
            report_name=report_name,
        )
