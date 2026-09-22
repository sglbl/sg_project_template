"""Inference service for fast online model predictions using ONNX Runtime."""

import time
from pathlib import Path
from typing import Any, Optional
import joblib
import numpy as np
from loguru import logger

from src.config import settings
from src.domain.schemas.ml_schemas import PredictRequest, PredictResponse
from src.infra.serving.onnx_engine import ONNXInferenceEngine


class InferenceService:
    """Production model inference service supporting ONNX and Scikit-Learn models."""

    def __init__(self, model_path: Optional[str] = None) -> None:
        self.artifacts_dir = Path(settings.MODEL_ARTIFACTS_DIR)
        self.active_model_path = model_path
        self._onnx_engine: Optional[ONNXInferenceEngine] = None
        self._fallback_model: Optional[Any] = None
        self._feature_names: list[str] = []

        self._load_active_model()

    def _load_active_model(self) -> None:
        """Attempt loading ONNX model first; fallback to .pkl if ONNX is unavailable."""
        target_path = Path(self.active_model_path) if self.active_model_path else None

        if not target_path or not target_path.exists():
            # Search artifacts directory for available .onnx or .pkl files
            onnx_files = list(self.artifacts_dir.glob("*.onnx"))
            if onnx_files:
                target_path = onnx_files[0]
            else:
                pkl_files = list(self.artifacts_dir.glob("*.pkl"))
                if pkl_files:
                    target_path = pkl_files[0]

        if target_path and target_path.exists():
            if target_path.suffix == ".onnx":
                try:
                    self._onnx_engine = ONNXInferenceEngine(str(target_path))
                    self.active_model_path = str(target_path)
                    logger.info(f"Loaded ONNX inference engine for {target_path}")
                    return
                except Exception as e:
                    logger.warning(f"Failed loading ONNX engine: {e}. Attempting fallback.")

            if target_path.suffix == ".pkl":
                loaded = joblib.load(target_path)
                if isinstance(loaded, dict) and "model" in loaded:
                    self._fallback_model = loaded["model"]
                    self._feature_names = loaded.get("features", [])
                else:
                    self._fallback_model = loaded
                self.active_model_path = str(target_path)
                logger.info(f"Loaded fallback Scikit-Learn model from {target_path}")

    def predict(self, request: PredictRequest) -> PredictResponse:
        """Execute single-sample or batch prediction."""
        start_time = time.perf_counter()

        if not self._onnx_engine and not self._fallback_model:
            self._load_active_model()

        if not self._onnx_engine and not self._fallback_model:
            raise RuntimeError("No active model loaded in InferenceService. Train or export a model first.")

        # Extract features array in consistent order
        try:
            if self._feature_names:
                features_vec = [float(request.features.get(f, 0.0)) for f in self._feature_names]
            else:
                features_vec = [float(val) for val in request.features.values()]
        except (ValueError, TypeError) as err:
            raise ValueError(f"All feature values must be numeric numbers. Error: {err}")

        input_arr = np.array([features_vec], dtype=np.float32)

        if self._onnx_engine:
            raw_pred = self._onnx_engine.predict(input_arr)
            prediction = int(raw_pred[0]) if hasattr(raw_pred[0], "__int__") else raw_pred[0]
        else:
            raw_pred = self._fallback_model.predict(input_arr)
            prediction = int(raw_pred[0]) if hasattr(raw_pred[0], "__int__") else raw_pred[0]

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        model_name = Path(self.active_model_path).stem if self.active_model_path else "active_model"
        return PredictResponse(
            prediction=prediction,
            model_name=model_name,
            model_version=request.model_version or "1.0.0",
            execution_time_ms=round(elapsed_ms, 2),
        )
