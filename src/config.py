from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    # LLM and API Urls
    OLLAMA_API_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: Optional[str] = None
    API_URL: str = "http://localhost:8100"

    # Database configuration
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5433"
    DB_NAME: str = "postgres"
    DB_SCHEMA: str = "example_schema"

    # MLOps, RustFS S3, & MLflow Configuration
    MLFLOW_TRACKING_URI: str = "http://localhost:5100"
    MLFLOW_EXPERIMENT_NAME: str = "default-experiment"
    RUSTFS_ENDPOINT_URL: str = "http://localhost:9010"
    AWS_ACCESS_KEY_ID: str = "rustfsadmin"
    AWS_SECRET_ACCESS_KEY: str = "rustfsadmin"
    RUSTFS_ACCESS_KEY: str = "rustfsadmin"
    RUSTFS_SECRET_KEY: str = "rustfsadmin"
    AWS_REGION: str = "us-east-1"
    
    # Path Configuration
    MODEL_ARTIFACTS_DIR: str = "data/models"
    DATA_RAW_DIR: str = "data/raw"
    DATA_PROCESSED_DIR: str = "data/processed"
    REPORTS_DIR: str = "data/reports"

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
        """ Use the default loading error, because of docker injections would take priority on docker """
        return init_settings, env_settings, dotenv_settings, file_secret_settings

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

# Create an instance of the Settings class
settings = Settings()


def generate_env_example(output_path: str | Path = ".env.example") -> str:
    """Generate a cleanly formatted .env.example by reading comments & fields directly from Settings source (SSOT)."""
    import inspect
    from pydantic_core import PydanticUndefined

    source = inspect.getsource(Settings)
    field_names = set(Settings.model_fields.keys())
    seen_fields: set[str] = set()

    output_lines: list[str] = [
        "# ===================================================================",
        "# Auto-generated from src/config.py (Settings SSOT)",
        "# Run './run export-env' to regenerate.",
        "# ===================================================================",
    ]
    comment_buffer: list[str] = []

    for line in source.splitlines():
        stripped = line.strip()
        # Stop before methods, properties, or inner configs
        if stripped.startswith(("def ", "@property", "@classmethod", "model_config")):
            break
        if stripped.startswith("#"):
            comment_buffer.append(stripped)
        elif not stripped:
            if comment_buffer and comment_buffer[-1] != "":
                comment_buffer.append("")
        elif ":" in stripped:
            var_name = stripped.split(":")[0].strip()
            if var_name in field_names:
                seen_fields.add(var_name)
                if comment_buffer:
                    if output_lines and output_lines[-1] != "":
                        output_lines.append("")
                    output_lines.extend(comment_buffer)
                    comment_buffer.clear()

                field_info = Settings.model_fields[var_name]
                default = field_info.default
                if var_name == "OPENAI_API_KEY":
                    val = '"sk-proj-..."'
                elif default is PydanticUndefined or default is None:
                    val = '""'
                elif isinstance(default, bool):
                    val = str(default).lower()
                else:
                    val = str(default)
                output_lines.append(f"{var_name}={val}")

    # Fallback for any fields not captured in class source lines
    unseen = [name for name in field_names if name not in seen_fields]
    if unseen:
        output_lines.append("")
        output_lines.append("# Additional Configuration")
        for name in unseen:
            field_info = Settings.model_fields[name]
            default = field_info.default
            val = str(default) if default not in (PydanticUndefined, None) else '""'
            output_lines.append(f"{name}={val}")

    content = "\n".join(output_lines).strip() + "\n"
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
    return content

