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
        )

        onnx_path: Optional[str] = None
        if export_onnx:
            try:
                onnx_path = self.export_pipe.export_to_onnx(pkl_path)
                metadata.artifact_path = onnx_path
            except Exception as e:
                logger.warning(f"Could not convert model to ONNX: {e}. Keeping .pkl artifact.")

        # Optional Model Registration
        if self.registry:
            version = self.registry.register_model(
                model_name=model_name,
                artifact_path=onnx_path or pkl_path,
                tags={"accuracy": f"{metadata.metrics.get('accuracy', 0.0):.4f}"},
            )
            self.registry.transition_stage(model_name, version, ModelStage.STAGING)
            metadata.version = version
            metadata.stage = ModelStage.STAGING

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
