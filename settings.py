"""Configuração centralizada — único lugar que lê o .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_POSTGRES_HOST: str
    DB_POSTGRES_PORT: int = 5432
    DB_POSTGRES_USER: str
    DB_POSTGRES_PASSWORD: str
    DB_POSTGRES_BUSINESS: str
    MCP_API_KEY: str
    PORT: int = 8001

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_POSTGRES_USER}:{self.DB_POSTGRES_PASSWORD}"
            f"@{self.DB_POSTGRES_HOST}:{self.DB_POSTGRES_PORT}/{self.DB_POSTGRES_BUSINESS}"
        )


settings = Settings()
