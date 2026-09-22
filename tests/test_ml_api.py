"""Tests for MLOps FastAPI REST API endpoints."""

from fastapi.testclient import TestClient
from src.presentation.rest.serve_api import app

client = TestClient(app)


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
