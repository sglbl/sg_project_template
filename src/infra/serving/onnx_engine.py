"""ONNX Runtime high-performance inference engine."""

from pathlib import Path
from typing import Any, Optional
import numpy as np
import onnxruntime as ort
from loguru import logger


class ONNXInferenceEngine:
    """Production serving engine powered by ONNX Runtime."""

    def __init__(self, model_path: str) -> None:
        self.model_path = model_path
        if not Path(model_path).exists():
            raise FileNotFoundError(f"ONNX model file not found: {model_path}")

        # Configure session options
        options = ort.SessionOptions()
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        options.intra_op_num_threads = 2

        self.session = ort.InferenceSession(model_path, options, providers=["CPUExecutionProvider"])
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]
        logger.info(f"Loaded ONNX model from {model_path} (Inputs: {self.input_names}, Outputs: {self.output_names})")

    def predict(self, input_data: np.ndarray | dict[str, np.ndarray]) -> np.ndarray:
        """Run inference over input numpy array or dictionary of named inputs."""
        if isinstance(input_data, np.ndarray):
            # Map single ndarray to primary input
            primary_input = self.input_names[0]
            feed_dict = {primary_input: input_data.astype(np.float32)}
        else:
            feed_dict = {k: v.astype(np.float32) for k, v in input_data.items()}

        outputs = self.session.run(self.output_names, feed_dict)
        return outputs[0]  # Return primary output
