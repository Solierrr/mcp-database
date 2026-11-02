"""Configuração centralizada — único lugar que lê o .env."""

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_TAMANHO_MINIMO_DA_CHAVE = 32


class Settings(BaseSettings):
    MCP_API_KEY: str | None = None
    SERVICE_KEY_AI_ASSISTANT: str | None = None
    SERVICE_KEY_AI_OPERATIONAL: str | None = None
    # Chave própria: enviada ao api-core e à api-recommendation. SERVICE_KEY_CORE é o nome antigo.
    SERVICE_KEY: str | None = Field(
        default=None, validation_alias=AliasChoices("SERVICE_KEY", "SERVICE_KEY_CORE")
    )
    PERSISTENCE_BASE_URL: str = "http://localhost:8080"
    RECOMMENDATION_API_URL: str = "http://localhost:8000"
    RECOMMENDATION_API_KEY: str | None = None
    PORT: int = 8001

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", populate_by_name=True
    )

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


settings = Settings()
