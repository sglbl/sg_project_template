"""FastAPI router for MLOps model serving, predictions, and drift monitoring."""

from pathlib import Path
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status
from loguru import logger

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

# Singleton service instance
_inference_service: Optional[InferenceService] = None


def get_inference_service() -> InferenceService:
    global _inference_service
    if _inference_service is None:
        _inference_service = InferenceService()
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
    return {
        "active_model_path": service.active_model_path,
        "engine": "ONNX Runtime" if service._onnx_engine else "Scikit-Learn Fallback",
        "artifacts_dir": str(service.artifacts_dir),
        "status": "ready" if (service._onnx_engine or service._fallback_model) else "no_model_loaded",
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
