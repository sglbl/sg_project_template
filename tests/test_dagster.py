"""Unit tests for Dagster orchestration assets and job definitions."""

import pytest
from dagster import materialize
from src.orchestration.dagster.definitions import defs, all_assets
from src.orchestration.dagster.jobs import mlops_pipeline_job, daily_retraining_schedule


def test_dagster_definitions_loaded():
    """Verify that all assets, jobs, and schedules are loaded properly in Definitions."""
    assert defs is not None

    asset_keys = {asset.key.to_user_string() for asset in all_assets}
    expected_assets = {
        "raw_iris_dataset",
        "data_splits",
        "trained_model",
        "onnx_model_artifact",
        "evidently_drift_report",
        "registered_model_version",
    }
    assert expected_assets.issubset(asset_keys)

    # Verify job and schedule
    assert mlops_pipeline_job.name == "mlops_pipeline_job"
    assert daily_retraining_schedule.name == "daily_retraining_schedule"
    assert daily_retraining_schedule.cron_schedule == "0 0 * * *"


def test_dagster_data_assets_materialization():
    """Verify in-memory materialization of the data engineering assets."""
    from src.orchestration.dagster.assets import raw_iris_dataset, data_splits

    result = materialize(
        [raw_iris_dataset, data_splits],
    )
    assert result.success
