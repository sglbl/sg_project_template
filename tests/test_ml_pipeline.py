"""Unit and integration tests for MLOps pipelines and inference service."""

import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from sklearn.datasets import load_iris

from src.application.pipelines.ingest import DataIngestionPipeline
from src.application.pipelines.train import ModelTrainingPipeline
from src.application.pipelines.export import ModelExportPipeline
from src.application.pipelines.evaluate import ModelEvaluationPipeline
from src.application.services.inference_service import InferenceService
from src.domain.schemas.ml_schemas import PredictRequest


@pytest.fixture
def sample_dataset(tmp_path: Path) -> tuple[str, str]:
    """Create sample iris dataset CSV files for testing."""
    iris = load_iris(as_frame=True)
    df = iris.frame.copy()
    df.columns = [c.replace(" (cm)", "").replace(" ", "_") for c in df.columns]

    raw_path = tmp_path / "iris_raw.csv"
    df.to_csv(raw_path, index=False)
    return str(raw_path), "target"


def test_data_ingestion_pipeline(sample_dataset: tuple[str, str], tmp_path: Path):
    raw_path, target_col = sample_dataset
    pipeline = DataIngestionPipeline()
    pipeline.processed_dir = tmp_path

    df = pipeline.load_data(raw_path)
    assert df.height == 150
    assert pipeline.validate_schema(df, target_col=target_col)

    train_path, test_path, metadata = pipeline.split_and_save(
        df, target_col=target_col, test_size=0.2, dataset_name="test_iris"
    )
    assert Path(train_path).exists()
    assert Path(test_path).exists()
    assert metadata.num_features == 4
    assert metadata.num_rows == 150


def test_model_training_and_export(sample_dataset: tuple[str, str], tmp_path: Path):
    raw_path, target_col = sample_dataset
    ingest_pipe = DataIngestionPipeline()
    ingest_pipe.processed_dir = tmp_path

    df = ingest_pipe.load_data(raw_path)
    train_path, test_path, _ = ingest_pipe.split_and_save(df, target_col=target_col, dataset_name="test_model")

    # Train
    train_pipe = ModelTrainingPipeline()
    train_pipe.artifacts_dir = tmp_path
    pkl_path, metadata = train_pipe.train_and_evaluate(
        train_path=train_path,
        test_path=test_path,
        target_col=target_col,
        model_name="iris_rf",
        tune=False,
    )
    assert Path(pkl_path).exists()
    assert metadata.metrics["accuracy"] >= 0.80

    # Export to ONNX
    export_pipe = ModelExportPipeline(artifacts_dir=str(tmp_path))
    onnx_path = export_pipe.export_to_onnx(pkl_path)
    assert Path(onnx_path).exists()

    # Test Inference Service with ONNX
    service = InferenceService(model_path=onnx_path)
    req = PredictRequest(
        features={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
    )
    res = service.predict(req)
    assert res.prediction in [0, 1, 2]
    assert res.execution_time_ms >= 0.0


def test_drift_evaluation(sample_dataset: tuple[str, str], tmp_path: Path):
    raw_path, _ = sample_dataset
    df = pd.read_csv(raw_path)

    ref_path = tmp_path / "ref.parquet"
    cur_path = tmp_path / "cur.parquet"

    df.iloc[:75].to_parquet(ref_path)
    df.iloc[75:].to_parquet(cur_path)

    eval_pipe = ModelEvaluationPipeline(reports_dir=str(tmp_path))
    drift_detected, drift_share, html_path = eval_pipe.run_drift_analysis(
        str(ref_path), str(cur_path), report_name="test_drift"
    )
    assert isinstance(drift_detected, bool)
    assert 0.0 <= drift_share <= 1.0
    assert Path(html_path).exists()
