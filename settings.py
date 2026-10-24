"""Configuração centralizada — único lugar que lê o .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_POSTGRES_HOST: str
    DB_POSTGRES_PORT: int = 5432
    DB_POSTGRES_USER: str
    DB_POSTGRES_PASSWORD: str
    DB_POSTGRES_BUSINESS: str
    MCP_API_KEY: str
    PERSISTENCE_BASE_URL: str = "http://localhost:8080"
    SERVICE_KEY_CORE: str
    RECOMMENDATION_API_URL: str = "http://localhost:8000"
    RECOMMENDATION_API_KEY: str | None = None
    PORT: int = 8001

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_POSTGRES_USER}:{self.DB_POSTGRES_PASSWORD}"
            f"@{self.DB_POSTGRES_HOST}:{self.DB_POSTGRES_PORT}/{self.DB_POSTGRES_BUSINESS}"
        )


settings = Settings()
