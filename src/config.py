from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from typing import Optional


class Settings(BaseSettings):
    # Database configuration
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "postgres"
    DB_SCHEMA: Optional[str] = "example_schema_name"
    OLLAMA_API_URL: str = "http://localhost:11434"

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
