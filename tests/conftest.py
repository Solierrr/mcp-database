"""Garante variáveis de ambiente mínimas para os testes, mesmo sem um .env
local — evita que settings.py quebre na coleta dos testes. Roda antes de
qualquer test module ser importado."""

import os

os.environ.setdefault("DATABASE_URL", "postgresql://fake:fake@localhost/fake")
os.environ.setdefault("MCP_API_KEY", "fake-key-for-tests")
