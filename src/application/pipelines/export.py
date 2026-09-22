"""Model serialization and ONNX format conversion pipeline."""

from pathlib import Path
from typing import Optional
import joblib
import numpy as np
from loguru import logger
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

from src.config import settings


class ModelExportPipeline:
    """Exports and serializes trained models into high-performance ONNX format."""

    def __init__(self, artifacts_dir: Optional[str] = None) -> None:
        self.artifacts_dir = Path(artifacts_dir or settings.MODEL_ARTIFACTS_DIR)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def export_to_onnx(
        self,
        model_pkl_path: str,
        output_onnx_path: Optional[str] = None,
    ) -> str:
        """Convert a scikit-learn pickled model to ONNX runtime format."""
        pkl_path = Path(model_pkl_path)
        if not pkl_path.exists():
            raise FileNotFoundError(f"Model pickle file not found: {model_pkl_path}")

        loaded = joblib.load(pkl_path)
        model = loaded["model"] if isinstance(loaded, dict) and "model" in loaded else loaded
        features = loaded.get("features", []) if isinstance(loaded, dict) else []
        num_features = len(features) if features else 4  # Default fallback

        # Define ONNX input tensor schema
        initial_type = [("float_input", FloatTensorType([None, num_features]))]

        logger.info(f"Converting model '{pkl_path.name}' to ONNX format (input dims: [None, {num_features}])...")
        onnx_model = convert_sklearn(model, initial_types=initial_type, target_opset=15)

        out_path = Path(output_onnx_path) if output_onnx_path else self.artifacts_dir / f"{pkl_path.stem}.onnx"
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "wb") as f:
            f.write(onnx_model.SerializeToString())

        logger.info(f"Exported ONNX model successfully to {out_path}")
        return str(out_path)
