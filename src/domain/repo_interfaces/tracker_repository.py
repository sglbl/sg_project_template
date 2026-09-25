"""Domain interface protocol for ML Experiment Tracking."""

from typing import Any, Optional, Protocol


class ITrackerRepository(Protocol):
    def start_run(self, run_name: Optional[str] = None, tags: Optional[dict[str, str]] = None) -> str:
        """Start a new experiment tracking run and return run_id."""
        ...

    def log_params(self, params: dict[str, Any]) -> None:
        """Log hyperparameter dictionary."""
        ...

    def log_metrics(self, metrics: dict[str, float], step: Optional[int] = None) -> None:
        """Log numerical evaluation metrics."""
        ...

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """Log local file artifact (e.g. plot, model file, JSON summary)."""
        ...

    def end_run(self) -> None:
        """End the active experiment run."""
        ...
