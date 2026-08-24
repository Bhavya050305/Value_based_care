"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


SUPPORTED_YEARS = [2022, 2023, 2024]

YEAR_TABLE_MAP = {
    2022: "aco_performance_2022",
    2023: "aco_performance_2023",
    2024: "aco_performance_2024",
}


class Settings(BaseSettings):
    """Runtime configuration for the VBC Command Center backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Value-Based Care Command Center API"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", description="development|staging|production")
    debug: bool = False
    supported_years: list[int] = Field(default_factory=lambda: [2022, 2023, 2024])
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="",
        description="Async PostgreSQL URL, e.g. postgresql+asyncpg://user:pass@host:5432/db",
    )
    database_ssl: bool = Field(
        default=False,
        description="Set to True only when the server certificate is trusted by the runtime.",
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = Field(
        default="",
        description="Server-side only. Never expose to frontend.",
    )
    supabase_jwt_secret: str = ""

    redis_url: str = "redis://localhost:6379/0"

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
    )

    llm_provider: str = Field(default="", description="Configured when AI integration is supplied.")
    llm_api_key: str = Field(default="", description="Server-side only.")
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = ""

    ml_artifacts_path: str = "app/ml/artifacts"
    ml_config_path: str = "app/ml/artifacts"

    log_level: str = "INFO"
    request_id_header: str = "X-Request-ID"


@lru_cache
def get_settings() -> Settings:
    return Settings()
