"""DuckDB and Polars analytical feature store provider."""

from pathlib import Path
from typing import Optional
from loguru import logger
import duckdb
import polars as pl

from src.config import settings


class DuckDBFeatureStore:
    """Embedded feature store powered by DuckDB and Polars."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        store_dir = Path(settings.DATA_PROCESSED_DIR)
        store_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path or str(store_dir / "feature_store.duckdb")
        self.conn = duckdb.connect(self.db_path)
        logger.info(f"Initialized DuckDB Feature Store at {self.db_path}")

    def save_features(self, table_name: str, df: pl.DataFrame) -> None:
        """Persist a Polars DataFrame as a feature table."""
        arrow_table = df.to_arrow()
        self.conn.register("temp_arrow_df", arrow_table)
        self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_arrow_df")
        self.conn.unregister("temp_arrow_df")
        logger.info(f"Saved {len(df)} rows into feature table '{table_name}'")

    def get_features(self, table_name: str, query: Optional[str] = None) -> pl.DataFrame:
        """Retrieve features as a Polars DataFrame."""
        sql = query or f"SELECT * FROM {table_name}"
        arrow_res = self.conn.execute(sql).arrow()
        return pl.from_arrow(arrow_res)  # type: ignore[return-value]

    def list_tables(self) -> list[str]:
        """List all available feature tables."""
        res = self.conn.execute("SHOW TABLES").fetchall()
        return [row[0] for row in res]
