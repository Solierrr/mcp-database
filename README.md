# api-mcp

Servidor MCP que expõe consultas ao Postgres de negócio da Solaria para o
`ai-assistant`, por meio do Model Context Protocol autenticado por API key.
Este repositório é somente de leitura e não é dono do schema; a referência
fica em `docs/schema_negocio.sql`.

[![License](https://img.shields.io/github/license/Solierrr/api-mcp)](https://github.com/Solierrr/api-mcp/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/Solierrr/api-mcp)](https://github.com/Solierrr/api-mcp/releases)

## O que ele entrega

O SDK `mcp`, servido por Starlette/Uvicorn, descobre funções Python decoradas
com `@mcp.tool()`. Assim, agentes consultam capacidades conhecidas em vez de
depender de endpoints REST customizados. O acesso ao PostgreSQL é isolado em
`postgres_client.py` e o endpoint `/mcp` exige API key.

Ferramentas disponíveis:

- `listar_ofertas_de_placas(potencia_minima_wp, marca)` — ofertas ativas com
  preço e fornecedor.
- `buscar_tecnicos_credenciados(profissao, cidade)` — técnicos afiliados a
  empresas e seus registros profissionais.

## Rodando localmente

1. Copie `.env.example` para `.env` e preencha `DATABASE_URL` e `MCP_API_KEY`.
2. Instale dependências com `pip install -r requirements.txt`.
3. Inicie com `python server.py`.

Para usar o padrão organizacional de ambiente, prefira `make env ENV=local`
antes do start.

## Docker

```sh
docker build -t api-mcp .
docker run --env-file .env -p 8001:8001 api-mcp
```

## Testes

```sh
python -m pytest tests -v
```

Os testes usam mocks e não requerem PostgreSQL nem um `.env` real.

## Documentação e contribuição

- [Arquitetura](./ARCHITECTURE.md)
- [Como executar](./RUNNING.md)
- [Guia de contribuição](./.github/CONTRIBUTING.md)
- [CODEOWNERS](./.github/CODEOWNERS)
