"""Model evaluation and data drift detection pipeline using Evidently."""

from pathlib import Path
from typing import Optional, Tuple
from loguru import logger
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

from src.config import settings
from src.domain.models.ml_entities import EvaluationReport


class ModelEvaluationPipeline:
    """Evaluates model performance and executes data & concept drift analysis."""

    def __init__(self, reports_dir: Optional[str] = None) -> None:
        self.reports_dir = Path(reports_dir or settings.REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run_drift_analysis(
        self,
        reference_data_path: str,
        current_data_path: str,
        report_name: str = "data_drift_report",
    ) -> Tuple[bool, float, str]:
        """Run Evidently DataDriftPreset on reference vs current datasets."""
        ref_path = Path(reference_data_path)
        cur_path = Path(current_data_path)

        if not ref_path.exists() or not cur_path.exists():
            raise FileNotFoundError(f"Dataset path missing: {ref_path} or {cur_path}")

        ref_df = pd.read_parquet(ref_path) if ref_path.suffix == ".parquet" else pd.read_csv(ref_path)
        cur_df = pd.read_parquet(cur_path) if cur_path.suffix == ".parquet" else pd.read_csv(cur_path)

        logger.info(f"Running Evidently drift report (Reference: {len(ref_df)} rows, Current: {len(cur_df)} rows)...")

        drift_report = Report(metrics=[DataDriftPreset()])
        drift_report.run(reference_data=ref_df, current_data=cur_df)

        # Save HTML and JSON reports
        html_out = self.reports_dir / f"{report_name}.html"
        json_out = self.reports_dir / f"{report_name}.json"

        drift_report.save_html(str(html_out))
        drift_report.save_json(str(json_out))

        # Parse drift summary from JSON dict
        report_dict = drift_report.as_dict()
        metrics = report_dict.get("metrics", [])
        drift_detected = False
        drift_share = 0.0

        for metric in metrics:
            result = metric.get("result", {})
            if "dataset_drift" in result:
                drift_detected = bool(result["dataset_drift"])
                drift_share = float(result.get("drift_share", 0.0))
                break

        logger.info(f"Drift Analysis Complete: Drift Detected = {drift_detected} (Share: {drift_share:.2%})")
        logger.info(f"Evidently HTML report saved to {html_out}")
        return drift_detected, drift_share, str(html_out)
