"""Central Dagster repository entrypoint exposing assets, jobs, and schedules."""

from dagster import Definitions, load_assets_from_modules

from src.orchestration.dagster import assets
from src.orchestration.dagster.jobs import mlops_pipeline_job, daily_retraining_schedule

# Load all assets declared in assets.py
all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    jobs=[mlops_pipeline_job],
    schedules=[daily_retraining_schedule],
)
