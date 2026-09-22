from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from typing import Optional


class Settings(BaseSettings):
    # Database configuration
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "postgres"
    DB_SCHEMA: str = "example_schema_name"
    OLLAMA_API_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: Optional[str] = None

    # MLOps & Experiment Tracking Configuration
    MLFLOW_TRACKING_URI: str = "http://localhost:5100"
    MLFLOW_EXPERIMENT_NAME: str = "default-experiment"
    RUSTFS_ENDPOINT_URL: str = "http://localhost:9010"
    MINIO_ENDPOINT_URL: Optional[str] = "http://localhost:9010"
    AWS_ACCESS_KEY_ID: str = "rustfsadmin"
    AWS_SECRET_ACCESS_KEY: str = "rustfsadmin"
    RUSTFS_ACCESS_KEY: str = "rustfsadmin"
    RUSTFS_SECRET_KEY: str = "rustfsadmin"
    AWS_REGION: str = "us-east-1"
    
    # Path Configuration
    MODEL_ARTIFACTS_DIR: str = "artifacts/models"
    DATA_RAW_DIR: str = "data/raw"
    DATA_PROCESSED_DIR: str = "data/processed"
    REPORTS_DIR: str = "artifacts/reports"

    # Logger
    LOG_LEVEL: str = "DEBUG"  
    
    # Sqlalchemy Logger
    SQLALCHEMY_LOG_LEVEL: bool = False

    # Computed properties
    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    @property
    def SYNC_DB_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    @property
    def DB_SCHEMA_URL(self) -> str:
        return f"{self.DB_URL}/{self.DB_SCHEMA}"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """ Increase the priority of the dotenv settings to load them first """
        return init_settings, dotenv_settings, env_settings, file_secret_settings

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

# Create an instance of the Settings class
settings = Settings()
