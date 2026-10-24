"""Garante variáveis de ambiente mínimas para os testes, mesmo sem um .env
local — evita que settings.py quebre na coleta dos testes. Roda antes de
qualquer test module ser importado."""

import os

os.environ.setdefault("MCP_API_KEY", "fake-key-for-tests")
os.environ.setdefault("SERVICE_KEY_CORE", "fake-service-key-for-tests")
