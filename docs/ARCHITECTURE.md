# Arquitetura do Repositório

O `api-mcp` segue uma arquitetura enxuta de três camadas dentro de um único processo Python: um servidor MCP (`server.py`) que registra ferramentas invocáveis por um agente de IA, um cliente HTTP do `api-core` (`core_client.py`) que isola as leituras de catálogo, e uma camada de configuração (`settings.py`) que centraliza a leitura de variáveis de ambiente via `pydantic-settings`. O servidor é montado como uma aplicação ASGI (`mcp.streamable_http_app()`) servida pelo Uvicorn, com um middleware Starlette de autenticação por API key protegendo o único endpoint HTTP exposto (`/mcp`). Não há camada de roteamento REST tradicional: a superfície pública do serviço é o conjunto de ferramentas MCP registradas, descobertas dinamicamente pelo cliente (o `ai-assistant`) via protocolo MCP, e não por URLs fixas documentadas em um contrato OpenAPI.

<p>
  <a href="https://github.com/syvixor/skills-icons">
    <img src="https://skills.syvixor.com/api/icons?i=python,fastapi" height="48" alt="Arquitetura do api-mcp">
  </a>
</p>

- **Arquitetura seguida**, servidor MCP single-process sobre Starlette/Uvicorn, com ferramentas registradas via decorator (`@mcp.tool()`) em vez de rotas HTTP tradicionais — o transporte é o protocolo MCP (`streamable_http_app`), não REST.
- **Ferramentas MCP expostas** (`server.py`), seis ferramentas registradas via `@mcp.tool()`:
  - `recomendar_ofertas`, `recomendar_profissionais` e `recomendar_fornecedores`, que não calculam ranking: chamam os feeds da `api-recommendation` por `recommendation_client.py` (HTTP, chave `X-Recommendation-Key`) e devolvem `fonte`, `avisos` e `itens` com métrica e motivos; falhas viram `{"erro": ...}`.
  - `listar_itens_de_fixacao`, lê as ofertas de infraestrutura em `GET /internal/catalog/infrastructure-offers` do `api-core` e devolve da mais barata para a mais cara; a `api-recommendation` ainda não ranqueia esses itens.
  - `listar_profissoes()`, lê `GET /internal/catalog/professions` e devolve id e nome, para filtrar `recomendar_profissionais`.
  - `buscar_tecnicos_credenciados(profissao: str = "", cidade: str = "")`, consulta `GET /internal/catalog/accredited-technicians`, retornando nome, empresa afiliada, tipo de afiliação, profissão, conselho e registro profissional, filtrando por profissão e/ou cidade da empresa afiliada.
- **Cliente do api-core** (`core_client.py`), `buscar_catalogo()` consulta `GET /internal/catalog/{recurso}` em `PERSISTENCE_BASE_URL` com o header `X-Service-Key` (`SERVICE_KEY_CORE`) e timeout, converte os campos do contrato (`camelCase`) para os campos de saída das ferramentas e devolve `{"erro": ...}` quando o `api-core` recusa a chave, responde com erro ou está fora do ar.
- **Middleware de autenticação** (`server.py`, classe `ExigirAPIKey`), um `BaseHTTPMiddleware` do Starlette que intercepta toda requisição ao app ASGI e retorna `401` com `{"erro": "API key ausente ou inválida"}` caso o header `x-api-key` não corresponda a `settings.MCP_API_KEY` — aplicado globalmente via `app.add_middleware(ExigirAPIKey)`, cobrindo o endpoint `/mcp` inteiro antes de qualquer ferramenta ser executada.
- **Configuração centralizada** (`settings.py`), classe `Settings(BaseSettings)` do `pydantic-settings` que lê `.env` e variáveis de ambiente (`MCP_API_KEY`, `PERSISTENCE_BASE_URL`, `SERVICE_KEY_CORE`, `RECOMMENDATION_API_URL`, `RECOMMENDATION_API_KEY`, `PORT`).
- **Testes** (`tests/`), `test_core_client.py` cobre o cliente do `api-core` (campos, filtros, chave, vazio e erros) com transporte HTTP falso; `test_server.py` cobre as ferramentas e os três cenários de autenticação (sem chave, chave errada, chave certa) usando `starlette.testclient.TestClient`; `test_recommendation_client.py` cobre o cliente da `api-recommendation` (campos, limite, chave, erros).

```Tree do Repositório
├── .github/
│   ├── CODEOWNERS
│   ├── CONTRIBUTING.md
│   └── pull_request_template.md
├── tests/
│   ├── test_core_client.py
│   ├── test_recommendation_client.py
│   └── test_server.py
├── .dockerignore
├── .editorconfig
├── .env.example
├── .gitattributes
├── .gitignore
├── README.md
├── ARCHITECTURE.md
├── RUNNING.md
├── LICENSE
├── core_client.py
├── recommendation_client.py
├── requirements.txt
├── server.py
└── settings.py
```
