from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)

    app_env: str = "development"
    api_gateway_key: str | None = Field(default=None, repr=False)
    workspace_ttl_hours: int = Field(default=24, ge=1, le=168)
    ai_calls_per_visitor: int = Field(default=10, ge=1, le=100)
    ai_calls_per_day: int = Field(default=100, ge=1, le=10000)
    app_mode: Literal["demo", "live"] = "demo"
    app_name: str = "HireMe AI"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql+asyncpg://hireme:hireme@localhost:5432/hireme"
    database_ssl: bool = False
    database_ssl_ca: str | None = None
    gemini_api_key: str | None = Field(default=None, repr=False)
    llm_provider: str = "gemini"
    llm_model: str = "gemini-3.1-flash-lite"
    embedding_model: str = "gemini-embedding-2"
    embedding_dim: int = 768
    frontend_url: str = "http://localhost:8501"
    allowed_origins: str = "http://localhost:8501"
    enable_live_job_discovery: bool = False
    enable_developer_mode: bool = True
    enable_langsmith: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "hireme-ai"
    max_upload_mb: int = Field(default=5, ge=1, le=20)
    http_timeout_seconds: float = Field(default=15, gt=0, le=60)

    @model_validator(mode="after")
    def production_requirements(self) -> "Settings":
        if self.app_env == "production":
            if not self.database_ssl:
                raise ValueError("Production requires DATABASE_SSL=true with verified TLS")
            if not self.api_gateway_key or len(self.api_gateway_key) < 32:
                raise ValueError(
                    "Production requires a random API_GATEWAY_KEY of at least 32 characters"
                )
            if self.app_mode != "live" or not self.gemini_api_key:
                raise ValueError("Production requires live mode and a Gemini key")
            if "localhost" in self.database_url or "127.0.0.1" in self.database_url:
                raise ValueError("Production requires an explicitly configured hosted database")
        return self

    @property
    def origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
