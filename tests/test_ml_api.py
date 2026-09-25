"""Tests for MLOps FastAPI REST API endpoints."""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.presentation.rest.serve_api import app
from src.config import settings
import src.presentation.rest.routers.ml as ml_router

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_test_model():
    """Ensure a trained model artifact exists using the project's real pipelines."""
    model_dir = Path(settings.MODEL_ARTIFACTS_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)
    has_model = bool(list(model_dir.glob("*.onnx")) or list(model_dir.glob("*.pkl")))
    if not has_model:
        from src.application.pipelines.ingest import DataIngestionPipeline
        from src.application.pipelines.train import ModelTrainingPipeline
        from src.application.pipelines.export import ModelExportPipeline

        raw_csv = Path(settings.DATA_RAW_DIR) / "iris.csv"
        ingest_pipe = DataIngestionPipeline()
        train_path, test_path, _ = ingest_pipe.split_and_save(
            ingest_pipe.load_data(str(raw_csv)), target_col="target"
        )
        train_pipe = ModelTrainingPipeline()
        pkl_path, _ = train_pipe.train_and_evaluate(
            train_path=train_path,
            test_path=test_path,
            target_col="target",
            model_name="random_forest",
        )
        export_pipe = ModelExportPipeline()
        export_pipe.export_to_onnx(pkl_path)
        ml_router._inference_service = None


def test_ml_model_metadata_endpoint():
    """Verify GET /ml/model returns active model status."""
    response = client.get("/ml/model")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "engine" in data
    assert "artifacts_dir" in data


def test_ml_predict_endpoint():
    """Verify POST /ml/predict executes inference successfully."""
    payload = {
        "features": {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
    }
    response = client.post("/ml/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "execution_time_ms" in data
    assert "model_name" in data
    assert data["prediction"] in [0, 1, 2]
    assert data["execution_time_ms"] >= 0.0
