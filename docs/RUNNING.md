<p align="center">
  <img src="../assets/readme/banners/mcp.png" alt="MCP" width="100%">
</p>

# Execução local

Use Python 3.14, conforme o Dockerfile, `make`, PostgreSQL acessível e Infisical CLI autenticado. O guia comum está em [PYTHON.md](https://github.com/Solierrr/docs-warehouse/blob/main/readme/running/PYTHON.md).

Execute `make install`, `make vault` e `make dev`, sabendo que a exportação usa as pastas `/database`, `/mcp` e `/service-keys`, e configure as variáveis do PostgreSQL, incluindo `DB_POSTGRES_BUSINESS`, as chaves dos chamadores e o endereço de recomendações.

| Comando | Efeito |
|---|---|
| `make test` | Pytest com clientes simulados |
| `make lint` | Ruff e verificação de formato |
| `make build` | Compila servidor, clientes e testes |
| `make dev` | Inicia o servidor na porta configurada, padrão 8001 |

Teste primeiro `/health` e `/ready`. Use um cliente MCP autenticado para descobrir e chamar ferramentas em `/mcp`. Não há `make openapi` ou Swagger, pois o catálogo de ferramentas é o contrato. Falhas de banco e divergência de schema devem ser verificadas antes do atendimento integrado.
