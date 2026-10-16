"""Dagster jobs and schedules orchestrating asset materialization."""

from dagster import (
    AssetSelection,
    ScheduleDefinition,
    define_asset_job,
)

# End-to-end MLOps pipeline job materializing all assets
mlops_pipeline_job = define_asset_job(
    name="mlops_pipeline_job",
    selection=AssetSelection.all(),
    description="End-to-end MLOps pipeline: Ingestion -> Split -> Train -> Export ONNX -> Drift Check -> Model Registry",
)

# Scheduled retraining job (e.g., daily at midnight)
daily_retraining_schedule = ScheduleDefinition(
    name="daily_retraining_schedule",
    job=mlops_pipeline_job,
    cron_schedule="0 0 * * *",
    description="Daily automated model retraining and drift monitoring pipeline.",
)
