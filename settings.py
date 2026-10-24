"""Configuração centralizada — único lugar que lê o .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MCP_API_KEY: str
    PERSISTENCE_BASE_URL: str = "http://localhost:8080"
    SERVICE_KEY_CORE: str
    RECOMMENDATION_API_URL: str = "http://localhost:8000"
    RECOMMENDATION_API_KEY: str | None = None
    PORT: int = 8001

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
