"""FastAPI router for MLOps model serving, predictions, and drift monitoring."""

from pathlib import Path
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status
from loguru import logger
from prometheus_client import Counter, Histogram, Gauge

from src.application.services.inference_service import InferenceService
from src.application.pipelines.evaluate import ModelEvaluationPipeline
from src.config import settings
from src.domain.schemas.ml_schemas import (
    PredictRequest,
    PredictResponse,
    DriftCheckRequest,
    DriftCheckResponse,
)

router = APIRouter(
    prefix="/ml",
    tags=["Machine Learning & Serving"],
)

# Custom Prometheus MLOps Metrics
ML_PREDICTIONS_TOTAL = Counter(
    "ml_predictions_total",
    "Total number of ML predictions served",
    ["model_name", "prediction_class"],
)

ML_INFERENCE_DURATION_SECONDS = Histogram(
    "ml_inference_duration_seconds",
    "Model inference execution duration in seconds",
    ["model_name"],
    buckets=(0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)

ML_MODEL_STATUS = Gauge(
    "ml_model_status",
    "Status of active ML model (1 = ready, 0 = not loaded)",
    ["engine", "model_name"],
)

ML_DATA_DRIFT_DETECTED = Gauge(
    "ml_data_drift_detected",
    "Whether dataset drift was detected in latest drift analysis (1 = detected, 0 = no drift)",
)

ML_DATA_DRIFT_SHARE = Gauge(
    "ml_data_drift_share",
    "Share of features with statistical drift detected (0.0 to 1.0)",
)

# Singleton service instance
_inference_service: Optional[InferenceService] = None


def _update_model_status_metric(service: InferenceService) -> None:
    """Update the Prometheus model status gauge based on the active inference service state."""
    engine_name = "ONNX Runtime" if service._onnx_engine else "Scikit-Learn Fallback"
    is_ready = bool(service._onnx_engine or service._fallback_model)
    model_name = Path(service.active_model_path).stem if service.active_model_path else "none"
    ML_MODEL_STATUS.labels(engine=engine_name, model_name=model_name).set(1 if is_ready else 0)
    # Initialize drift gauges if not set
    try:
        ML_DATA_DRIFT_DETECTED.set(0)
        ML_DATA_DRIFT_SHARE.set(0.0)
    except Exception:
        pass


def get_inference_service() -> InferenceService:
    global _inference_service
    if _inference_service is None:
        _inference_service = InferenceService()
        _update_model_status_metric(_inference_service)
    return _inference_service


@router.post(
    "/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Run model prediction",
    description="Execute low-latency model inference using the active ONNX or Scikit-Learn model.",
)
async def predict_endpoint(request: PredictRequest) -> PredictResponse:
    """Run real-time inference on input feature dictionary."""
    try:
        service = get_inference_service()
        response = service.predict(request)

        # Record Prometheus MLOps telemetry
        model_name = response.model_name or "unknown"
        pred_class = str(response.prediction)
        ML_PREDICTIONS_TOTAL.labels(model_name=model_name, prediction_class=pred_class).inc()
        ML_INFERENCE_DURATION_SECONDS.labels(model_name=model_name).observe(response.execution_time_ms / 1000.0)

        return response
    except ValueError as e:
        logger.warning(f"Prediction input validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failed: {str(e)}",
        )


@router.get(
    "/model",
    summary="Get active model metadata",
    description="Returns active inference engine status, model artifact path, and format.",
)
async def get_active_model() -> dict[str, Any]:
    """Retrieve active model information."""
    service = get_inference_service()
    engine_name = "ONNX Runtime" if service._onnx_engine else "Scikit-Learn Fallback"
    is_ready = bool(service._onnx_engine or service._fallback_model)
    model_name = Path(service.active_model_path).stem if service.active_model_path else "none"
    ML_MODEL_STATUS.labels(engine=engine_name, model_name=model_name).set(1 if is_ready else 0)

    return {
        "active_model_path": service.active_model_path,
        "engine": engine_name,
        "artifacts_dir": str(service.artifacts_dir),
        "status": "ready" if is_ready else "no_model_loaded",
    }


@router.post(
    "/drift",
    response_model=DriftCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Check data drift",
    description="Evaluate feature and target drift between baseline reference data and current incoming data using Evidently.",
)
async def check_drift_endpoint(request: DriftCheckRequest) -> DriftCheckResponse:
    """Run Evidently drift detection between reference and current datasets."""
    try:
        eval_pipe = ModelEvaluationPipeline()
        drift_detected, drift_share, html_path = eval_pipe.run_drift_analysis(
            reference_data_path=request.reference_data_path,
            current_data_path=request.current_data_path,
            report_name="api_drift_report",
        )

        # Record Prometheus drift telemetry
        ML_DATA_DRIFT_DETECTED.set(1 if drift_detected else 0)
        ML_DATA_DRIFT_SHARE.set(float(drift_share))

        return DriftCheckResponse(
            drift_detected=drift_detected,
            drift_share=round(drift_share, 4),
            report_html_path=html_path,
        )
    except Exception as e:
        logger.error(f"Drift endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Drift evaluation failed: {str(e)}",
        )
