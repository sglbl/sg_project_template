"""Dagster Software-Defined Assets (SDAs) orchestrating the end-to-end MLOps lifecycle."""

from pathlib import Path
from typing import Dict, Any
from dagster import asset, AssetExecutionContext, Output, MetadataValue

from src.config import settings
from src.application.pipelines.ingest import DataIngestionPipeline
from src.application.pipelines.train import ModelTrainingPipeline
from src.application.pipelines.export import ModelExportPipeline
from src.application.pipelines.evaluate import ModelEvaluationPipeline
from src.infra.ml.mlflow_tracker import MLflowTracker
from src.domain.models.ml_entities import ModelStage


@asset(
    group_name="data_engineering",
    description="Loads raw data, verifies schema integrity, and ensures dataset presence.",
)
def raw_iris_dataset(context: AssetExecutionContext) -> str:
    """Ensure raw dataset exists and passes schema validation."""
    data_path = Path(settings.DATA_RAW_DIR) / "iris.csv"

    # Auto-generate sample dataset if missing
    if not data_path.exists():
        from sklearn.datasets import load_iris
        data_path.parent.mkdir(parents=True, exist_ok=True)
        iris = load_iris(as_frame=True)
        df_iris = iris.frame.copy()
        df_iris.columns = [c.replace(" (cm)", "").replace(" ", "_") for c in df_iris.columns]
        df_iris.to_csv(data_path, index=False)
        context.log.info(f"Generated sample Iris dataset at {data_path}")

    pipeline = DataIngestionPipeline()
    df = pipeline.load_data(str(data_path))
    pipeline.validate_schema(df, target_col="target")

    context.log.info(f"Raw dataset validated: {df.height} rows, {df.width} columns")
    return str(data_path)


@asset(
    group_name="data_engineering",
    description="Stratified train/test dataset partition persisted as Parquet files.",
)
def data_splits(context: AssetExecutionContext, raw_iris_dataset: str) -> Output[Dict[str, Any]]:
    """Split raw data into stratified train and test sets."""
    pipeline = DataIngestionPipeline()
    df = pipeline.load_data(raw_iris_dataset)
    train_path, test_path, metadata = pipeline.split_and_save(
        df=df,
        target_col="target",
        test_size=0.2,
        dataset_name="dataset",
    )

    context.log.info(f"Created dataset splits: train={train_path}, test={test_path}")

    return Output(
        value={
            "train_path": train_path,
            "test_path": test_path,
            "version": metadata.version,
            "num_rows": metadata.num_rows,
            "num_features": metadata.num_features,
            "feature_names": metadata.feature_names,
        },
        metadata={
            "dataset_version": MetadataValue.text(metadata.version),
            "total_rows": MetadataValue.int(metadata.num_rows),
            "num_features": MetadataValue.int(metadata.num_features),
            "feature_names": MetadataValue.json(metadata.feature_names),
            "train_path": MetadataValue.path(train_path),
            "test_path": MetadataValue.path(test_path),
        },
    )


@asset(
    group_name="model_training",
    description="Trains Random Forest with MLflow tracking and hyperparameter evaluation.",
)
def trained_model(context: AssetExecutionContext, data_splits: Dict[str, Any]) -> Output[Dict[str, Any]]:
    """Train machine learning model and record metrics in MLflow."""
    train_path = str(data_splits["train_path"])
    test_path = str(data_splits["test_path"])

    tracker = MLflowTracker()
    training_pipe = ModelTrainingPipeline(tracker=tracker)

    model_name = "random_forest"
    context.log.info(f"Training model '{model_name}' on {train_path}...")

    pkl_path, metadata = training_pipe.train_and_evaluate(
        train_path=train_path,
        test_path=test_path,
        target_col="target",
        model_name=model_name,
        tune=False,
        close_run=False,
    )

    context.log.info(f"Trained model metrics: {metadata.metrics}")

    accuracy = float(metadata.metrics.get("accuracy", 0.0))
    precision = float(metadata.metrics.get("precision", 0.0))
    recall = float(metadata.metrics.get("recall", 0.0))
    f1_score = float(metadata.metrics.get("f1_score", 0.0))

    run_id = metadata.version

    return Output(
        value={
            "model_name": model_name,
            "pkl_path": pkl_path,
            "run_id": run_id,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
        },
        metadata={
            "model_name": MetadataValue.text(model_name),
            "pkl_path": MetadataValue.path(pkl_path),
            "run_id": MetadataValue.text(run_id),
            "accuracy": MetadataValue.float(accuracy),
            "precision": MetadataValue.float(precision),
            "recall": MetadataValue.float(recall),
            "f1_score": MetadataValue.float(f1_score),
        },
    )


@asset(
    group_name="model_serving",
    description="Converts trained Scikit-Learn model to optimized ONNX computational graph.",
)
def onnx_model_artifact(context: AssetExecutionContext, trained_model: Dict[str, Any]) -> Output[Dict[str, Any]]:
    """Export trained model to high-performance ONNX format."""
    pkl_path = str(trained_model["pkl_path"])
    export_pipe = ModelExportPipeline()

    onnx_path = export_pipe.export_to_onnx(pkl_path)
    context.log.info(f"Exported model to ONNX runtime format at {onnx_path}")

    # Log to MLflow if run is active
    tracker = MLflowTracker()
    try:
        tracker.log_artifact(onnx_path)
    except Exception as e:
        context.log.warning(f"Could not log ONNX artifact to MLflow: {e}")

    return Output(
        value={
            "onnx_path": onnx_path,
            "pkl_path": pkl_path,
            "framework": "ONNX Runtime",
        },
        metadata={
            "onnx_path": MetadataValue.path(onnx_path),
            "framework": MetadataValue.text("ONNX Runtime"),
            "source_model": MetadataValue.path(pkl_path),
        },
    )


@asset(
    group_name="monitoring",
    description="Evaluates data & prediction drift using Evidently and produces HTML report.",
)
def evidently_drift_report(context: AssetExecutionContext, data_splits: Dict[str, Any]) -> Output[Dict[str, Any]]:
    """Detect statistical distribution drift between reference (train) and current (test) datasets."""
    train_path = str(data_splits["train_path"])
    test_path = str(data_splits["test_path"])

    eval_pipe = ModelEvaluationPipeline()
    report_name = "dagster_drift_report"
    drift_detected, drift_score, report_path = eval_pipe.run_drift_analysis(
        reference_data_path=train_path,
        current_data_path=test_path,
        report_name=report_name,
    )

    context.log.info(f"Drift evaluation completed: detected={drift_detected}, drift_score={drift_score:.4f}")

    return Output(
        value={
            "drift_detected": drift_detected,
            "drift_score": drift_score,
            "report_path": report_path,
        },
        metadata={
            "drift_detected": MetadataValue.bool(drift_detected),
            "drift_score": MetadataValue.float(drift_score),
            "report_path": MetadataValue.path(report_path),
        },
    )


@asset(
    group_name="model_serving",
    description="Registers the verified ONNX model to MLflow Model Registry and transitions to Staging.",
)
def registered_model_version(
    context: AssetExecutionContext,
    trained_model: Dict[str, Any],
    onnx_model_artifact: Dict[str, Any],
) -> Output[Dict[str, Any]]:
    """Register verified model in MLflow Model Registry and publish to S3/RustFS storage."""
    model_name = str(trained_model["model_name"])
    onnx_path = str(onnx_model_artifact["onnx_path"])
    accuracy = float(trained_model["accuracy"])

    tracker = MLflowTracker()
    registry_tags = {
        "framework": "onnx",
        "orchestrator": "dagster",
        "accuracy": f"{accuracy:.4f}",
    }

    version = tracker.register_model(
        model_name=model_name,
        artifact_path=onnx_path,
        tags=registry_tags,
        description=f"Dagster orchestrated model release (Accuracy: {accuracy:.4f})",
    )
    tracker.transition_stage(model_name, version, ModelStage.STAGING)
    context.log.info(f"Successfully registered model '{model_name}' version {version} -> STAGING")

    # Upload to RustFS / S3 storage
    storage_url = "local"
    try:
        from src.infra.ml.storage import S3StorageProvider
        storage = S3StorageProvider()
        remote_key = f"models/{model_name}/{version}/{Path(onnx_path).name}"
        storage_url = storage.upload_file(onnx_path, remote_key)
        context.log.info(f"Published ONNX model to remote storage at {storage_url}")
    except Exception as e:
        context.log.warning(f"Could not upload model to S3/RustFS: {e}")

    tracker.end_run()

    return Output(
        value={
            "registered_model_name": model_name,
            "version": version,
            "stage": "Staging",
            "storage_url": storage_url,
        },
        metadata={
            "registered_model_name": MetadataValue.text(model_name),
            "version": MetadataValue.text(version),
            "stage": MetadataValue.text("Staging"),
            "storage_url": MetadataValue.text(storage_url),
        },
    )
