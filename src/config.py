from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Database configuration
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "postgres"
    DB_SCHEMA: Optional[str] = "example_schema_name"

    # Logger
    LOG_LEVEL: str = "DEBUG"  
    
    # Sqlalchemy Logger
    SQLALCHEMY_DEBUG_LOG: bool = False

    # Computed properties
    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    @property
    def DB_SCHEMA_URL(self) -> str:
        return f"{self.DB_URL}/{self.DB_SCHEMA}"

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

# Create an instance of the Settings class
settings = Settings()
