"""Garante variáveis de ambiente mínimas para os testes, mesmo sem um .env
local — evita que settings.py quebre na coleta dos testes. Roda antes de
qualquer test module ser importado."""

import os

os.environ.setdefault("DB_POSTGRES_HOST", "localhost")
os.environ.setdefault("DB_POSTGRES_USER", "fake")
os.environ.setdefault("DB_POSTGRES_PASSWORD", "fake")
os.environ.setdefault("DB_POSTGRES_BUSINESS", "fake")
os.environ.setdefault("MCP_API_KEY", "fake-key-for-tests")
os.environ.setdefault("SERVICE_KEY_AI_ASSISTANT", "chave-de-teste-do-ai-assistant-0001")
os.environ.setdefault(
    "SERVICE_KEY_AI_OPERATIONAL", "chave-de-teste-do-ai-operational-01"
)
