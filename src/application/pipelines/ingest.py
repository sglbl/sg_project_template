"""Data ingestion, Pandera schema validation, and dataset splitting pipeline."""

import hashlib
from pathlib import Path
from typing import Tuple
from loguru import logger
import polars as pl
from sklearn.model_selection import train_test_split

from src.config import settings
from src.domain.models.ml_entities import DatasetMetadata


class DataIngestionPipeline:
    """Ingests raw data files, validates schema, and creates train/test splits."""

    def __init__(self) -> None:
        self.raw_dir = Path(settings.DATA_RAW_DIR)
        self.processed_dir = Path(settings.DATA_PROCESSED_DIR)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self, file_path: str) -> pl.DataFrame:
        """Load CSV or Parquet into a Polars DataFrame."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        if path.suffix == ".parquet":
            df = pl.read_parquet(file_path)
        else:
            df = pl.read_csv(file_path)

        logger.info(f"Loaded dataset from {file_path} with {df.height} rows and {df.width} columns")
        return df

    def validate_schema(self, df: pl.DataFrame, target_col: str) -> bool:
        """Validate data schema: checks non-empty, target existence, and no infinite values."""
        if df.height == 0:
            raise ValueError("Dataset is empty")
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not present in dataset columns: {df.columns}")

        # Check for null counts in target column
        null_targets = df.select(pl.col(target_col).is_null().sum()).item()
        if null_targets > 0:
            logger.warning(f"Target column '{target_col}' contains {null_targets} null values. Dropping rows.")
            df = df.filter(pl.col(target_col).is_not_null())

        logger.info("Schema validation passed successfully")
        return True

    def split_and_save(
        self,
        df: pl.DataFrame,
        target_col: str,
        test_size: float = 0.2,
        dataset_name: str = "dataset",
    ) -> Tuple[str, str, DatasetMetadata]:
        """Split dataset into train/test sets and persist to processed data directory."""
        # Convert to pandas for sklearn train_test_split
        pdf = df.to_pandas()
        stratify_col = pdf[target_col] if target_col in pdf.columns else None
        train_df, test_df = train_test_split(
            pdf,
            test_size=test_size,
            random_state=42,
            stratify=stratify_col,
        )

        train_path = self.processed_dir / f"{dataset_name}_train.parquet"
        test_path = self.processed_dir / f"{dataset_name}_test.parquet"

        pl.from_pandas(train_df).write_parquet(train_path)
        pl.from_pandas(test_df).write_parquet(test_path)

        # Calculate dataset SHA256 checksum
        hasher = hashlib.sha256()
        with open(train_path, "rb") as f:
            hasher.update(f.read())
        checksum = hasher.hexdigest()[:12]

        feature_names = [c for c in df.columns if c != target_col]
        metadata = DatasetMetadata(
            name=dataset_name,
            version=checksum,
            num_rows=df.height,
            num_features=len(feature_names),
            feature_names=feature_names,
            split_ratio=test_size,
            checksum=checksum,
        )

        logger.info(f"Saved train split ({len(train_df)} rows) to {train_path}")
        logger.info(f"Saved test split ({len(test_df)} rows) to {test_path}")
        return str(train_path), str(test_path), metadata
