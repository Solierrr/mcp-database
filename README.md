# api-mcp

Servidor MCP que expõe consultas ao Postgres de negócio da Solaria para o
`ai-assistant` e o `ai-operational`, por meio do Model Context Protocol autenticado
por chave de serviço (`X-Service-Key`).
Este repositório é somente de leitura e não é dono do schema; a fonte do
schema é o `database-console` (`db/core/schema.sql` e as migrations em `db/core/migrations`).
O acesso ao banco deve usar o usuário somente leitura `solaria_ro_mcp` (contrato em
`db/roles/contracts.json` do `database-console`).

[![License](https://img.shields.io/github/license/Solierrr/api-mcp)](https://github.com/Solierrr/api-mcp/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/Solierrr/api-mcp)](https://github.com/Solierrr/api-mcp/releases)

## O que ele entrega

O SDK `mcp`, servido por Starlette/Uvicorn, descobre funções Python decoradas
com `@mcp.tool()`. Assim, agentes consultam capacidades conhecidas em vez de
depender de endpoints REST customizados. O acesso ao PostgreSQL é isolado em
`postgres_client.py` e o endpoint `/mcp` exige a chave de serviço de um dos
agentes (`SERVICE_KEY_AI_ASSISTANT` ou `SERVICE_KEY_AI_OPERATIONAL`). Enquanto os
agentes migram, a chave antiga `x-api-key` (`MCP_API_KEY`) continua aceita se
estiver configurada.

Ferramentas disponíveis:

- `recomendar_ofertas(estrategia, unidade_id, limite)` — top-N de ofertas de
  placas ranqueado pela `api-recommendation` (`best_value`, `most_efficient`,
  `nearest_available`, `most_proven`).
- `recomendar_profissionais(estrategia, profissao_id, limite)` — top-N de
  profissionais (`best_match`, `top_rated`, `most_qualified`,
  `most_experienced`, `most_reliable`).
- `recomendar_fornecedores(estrategia, unidade_id, limite)` — top-N de empresas
  fornecedoras (`most_proven`, `broadest_catalog`, `nearest`).
- `listar_itens_de_fixacao(tipo, marca, limite)` — ofertas de itens de fixação (trilho,
  grampo, suporte, gancho, kit) por preço, sem ranking por mérito (consulta direta ao Postgres).
- `listar_profissoes()` — profissões e ids, para filtrar os profissionais.
- `buscar_tecnicos_credenciados(profissao, cidade)` — técnicos afiliados a
  empresas e seus registros profissionais (consulta direta ao Postgres).

As ferramentas `recomendar_*` não calculam ranking: chamam os feeds da
`api-recommendation` (`RECOMMENDATION_API_URL`, com `X-Service-Key` lido de
`SERVICE_KEY`) e
devolvem `fonte`, `avisos` e `itens` com a métrica e os motivos de cada
posição. Se o serviço falhar, devolvem `{"erro": ...}` para o agente explicar.

## Rodando localmente

1. Copie `.env.example` para `.env` e preencha o Postgres (`DB_POSTGRES_*`) e as
   chaves de serviço, ou gere o arquivo com `make env ENV=local`.
2. Instale dependências com `pip install -r requirements.txt`.
3. Inicie com `python server.py`.

Para usar o padrão organizacional de ambiente, prefira `make env ENV=local`
antes do start.

## Saúde e versão

- `GET /health`: processo vivo, com a versão do release (`{"status":"UP","version":"X.Y.Z"}`).
- `GET /ready`: pronto para atender; consulta o Postgres com timeout de 2 segundos e
  responde 503 (`{"status":"DOWN"}`) se o banco não responder.
- As duas rotas são públicas. A versão vem do `version.txt`, atualizado pelo
  release-please, e também aparece no log de partida.

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
