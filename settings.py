"""Configuração centralizada — único lugar que lê o .env."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_TAMANHO_MINIMO_DA_CHAVE = 32


class Settings(BaseSettings):
    DB_POSTGRES_HOST: str
    DB_POSTGRES_PORT: int = 5432
    DB_POSTGRES_USER: str
    DB_POSTGRES_PASSWORD: str
    DB_POSTGRES_BUSINESS: str
    MCP_API_KEY: str | None = None
    SERVICE_KEY_AI_ASSISTANT: str | None = None
    SERVICE_KEY_AI_OPERATIONAL: str | None = None
    SERVICE_KEY: str | None = None
    RECOMMENDATION_API_URL: str = "http://localhost:8000"
    RECOMMENDATION_API_KEY: str | None = None
    PORT: int = 8001

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator(
        "SERVICE_KEY_AI_ASSISTANT", "SERVICE_KEY_AI_OPERATIONAL", "SERVICE_KEY"
    )
    @classmethod
    def _chave_longa(cls, valor: str | None) -> str | None:
        if valor and len(valor) < _TAMANHO_MINIMO_DA_CHAVE:
            raise ValueError(
                f"a chave de serviço precisa de ao menos {_TAMANHO_MINIMO_DA_CHAVE} caracteres"
            )
        return valor

    @property
    def service_keys(self) -> dict[str, str]:
        chaves = {
            "ai-assistant": self.SERVICE_KEY_AI_ASSISTANT,
            "ai-operational": self.SERVICE_KEY_AI_OPERATIONAL,
        }
        return {chamador: chave for chamador, chave in chaves.items() if chave}

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_POSTGRES_USER}:{self.DB_POSTGRES_PASSWORD}"
            f"@{self.DB_POSTGRES_HOST}:{self.DB_POSTGRES_PORT}/{self.DB_POSTGRES_BUSINESS}"
        )


settings = Settings()
