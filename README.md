# api-mcp

Servidor MCP que expõe consultas de catálogo da Solaria para o `ai-assistant`,
por meio do Model Context Protocol autenticado por API key. Este repositório é
somente de leitura e não acessa banco de dados: as consultas passam pelos
endpoints internos `GET /internal/catalog/**` do `api-core`, autenticados por
`X-Service-Key`.

[![License](https://img.shields.io/github/license/Solierrr/api-mcp)](https://github.com/Solierrr/api-mcp/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/Solierrr/api-mcp)](https://github.com/Solierrr/api-mcp/releases)

## O que ele entrega

O SDK `mcp`, servido por Starlette/Uvicorn, descobre funções Python decoradas
com `@mcp.tool()`. Assim, agentes consultam capacidades conhecidas em vez de
depender de endpoints REST customizados. O acesso ao `api-core` é isolado em
`core_client.py` e o endpoint `/mcp` exige API key.

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
  grampo, suporte, gancho, kit) por preço, sem ranking por mérito (`GET /internal/catalog/infrastructure-offers`).
- `listar_profissoes()` — profissões e ids, para filtrar os profissionais
  (`GET /internal/catalog/professions`).
- `buscar_tecnicos_credenciados(profissao, cidade)` — técnicos afiliados a
  empresas e seus registros profissionais (`GET /internal/catalog/accredited-technicians`).

As ferramentas `recomendar_*` não calculam ranking: chamam os feeds da
`api-recommendation` (`RECOMMENDATION_API_URL`, `RECOMMENDATION_API_KEY`) e
devolvem `fonte`, `avisos` e `itens` com a métrica e os motivos de cada
posição. Se o serviço falhar, devolvem `{"erro": ...}` para o agente explicar.

`listar_profissoes`, `listar_itens_de_fixacao` e `buscar_tecnicos_credenciados`
chamam o `api-core` (`PERSISTENCE_BASE_URL`, chave em `SERVICE_KEY_CORE`
enviada no header `X-Service-Key`) e mantêm os campos de saída em português.
Se o `api-core` recusar a chave ou estiver fora do ar, devolvem
`{"erro": ...}`.

## Rodando localmente

1. Copie `.env.example` para `.env` e preencha `MCP_API_KEY`, `PERSISTENCE_BASE_URL` e `SERVICE_KEY_CORE`.
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

Os testes simulam o `api-core` com um transporte HTTP falso e não requerem o
`api-core` no ar nem um `.env` real.

## Documentação e contribuição

- [Arquitetura](./ARCHITECTURE.md)
- [Como executar](./RUNNING.md)
- [Guia de contribuição](./.github/CONTRIBUTING.md)
- [CODEOWNERS](./.github/CODEOWNERS)
