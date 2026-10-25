# Arquitetura do Repositório

O `api-mcp` segue uma arquitetura enxuta de três camadas dentro de um único processo Python: um servidor MCP (`server.py`) que registra ferramentas invocáveis por um agente de IA, uma camada de acesso a dados (`postgres_client.py`) que isola o pool de conexões com o Postgres "Negócio", e uma camada de configuração (`settings.py`) que centraliza a leitura de variáveis de ambiente via `pydantic-settings`. O servidor é montado como uma aplicação ASGI (`mcp.streamable_http_app()`) servida pelo Uvicorn, com um middleware Starlette de autenticação por chave de serviço protegendo o endpoint `/mcp`, além das rotas públicas de saúde `/health` e `/ready`. Não há camada de roteamento REST tradicional: a superfície pública do serviço é o conjunto de ferramentas MCP registradas, descobertas dinamicamente pelo cliente (o `ai-assistant`) via protocolo MCP, e não por URLs fixas documentadas em um contrato OpenAPI.

<p>
  <a href="https://github.com/syvixor/skills-icons">
    <img src="https://skills.syvixor.com/api/icons?i=python,postgres,fastapi" height="48" alt="Arquitetura do api-mcp">
  </a>
</p>

- **Arquitetura seguida**, servidor MCP single-process sobre Starlette/Uvicorn, com ferramentas registradas via decorator (`@mcp.tool()`) em vez de rotas HTTP tradicionais — o transporte é o protocolo MCP (`streamable_http_app`), não REST.
- **Ferramentas MCP expostas** (`server.py`), seis ferramentas registradas via `@mcp.tool()`:
  - `recomendar_ofertas`, `recomendar_profissionais` e `recomendar_fornecedores`, que não calculam ranking: chamam os feeds da `api-recommendation` por `recommendation_client.py` (HTTP, chave `X-Service-Key` lida de `SERVICE_KEY`; a antiga `X-Recommendation-Key` só vai junto enquanto `RECOMMENDATION_API_KEY` estiver configurada) e devolvem `fonte`, `avisos` e `itens` com métrica e motivos; falhas viram `{"erro": ...}`.
  - `listar_itens_de_fixacao`, lê as ofertas com `product_type = INFRASTRUCTURE` do Postgres e devolve da mais barata para a mais cara; a `api-recommendation` ainda não ranqueia esses itens.
  - `listar_profissoes()`, lê `profession` do Postgres e devolve id e nome, para filtrar `recomendar_profissionais`.
  - `buscar_tecnicos_credenciados(profissao: str = "", cidade: str = "")`, consulta técnicos credenciados afiliados a empresas técnicas, retornando nome, empresa afiliada, tipo de afiliação, profissão, conselho e registro profissional, filtrando por profissão e/ou cidade da empresa afiliada.
- **Camada de acesso ao Postgres** (`postgres_client.py`), um `psycopg2.pool.ThreadedConnectionPool` (1 a 10 conexões) instanciado sob demanda (lazy, em `_get_pool()`) e reaproveitado entre chamadas; o context manager `get_cursor()` entrega um cursor `RealDictCursor` (linhas como `dict`), faz `commit()` em caso de sucesso e `rollback()` em caso de exceção, sempre devolvendo a conexão ao pool no `finally`.
- **Middleware de autenticação** (`server.py`, classe `ExigirChaveDeServico`), um `BaseHTTPMiddleware` do Starlette que intercepta toda requisição ao app ASGI, exceto `/health` e `/ready`. Compara o `X-Service-Key` em tempo constante (`hmac.compare_digest`) com as chaves dos agentes aceitos (`SERVICE_KEY_AI_ASSISTANT` e `SERVICE_KEY_AI_OPERATIONAL`); chave ausente ou inválida responde `401` `UNAUTHENTICATED` e chamador conhecido fora da rota responde `403` `FORBIDDEN`, os dois em `application/problem+json`. Durante a migração dos agentes, o `x-api-key` antigo (`MCP_API_KEY`) também é aceito, só se estiver configurado; sem nenhuma chave configurada, tudo é recusado.
- **Saúde e versão** (`server.py` e `version.py`), `/health` responde `{"status":"UP","version":...}` sem consultar dependências e `/ready` faz `SELECT 1` no Postgres por uma conexão própria com timeout de 2 segundos (`postgres_client.ping`), respondendo `503` `{"status":"DOWN"}` se falhar; a versão vem do `version.txt` (atualizado pelo release-please) e aparece também no log de partida.
- **Configuração centralizada** (`settings.py`), classe `Settings(BaseSettings)` do `pydantic-settings` que lê `.env` e variáveis de ambiente (`DB_POSTGRES_HOST`, `DB_POSTGRES_PORT`, `DB_POSTGRES_USER`, `DB_POSTGRES_PASSWORD`, `DB_POSTGRES_BUSINESS`, `SERVICE_KEY_AI_ASSISTANT`, `SERVICE_KEY_AI_OPERATIONAL`, `SERVICE_KEY`, `MCP_API_KEY`, `RECOMMENDATION_API_URL`, `RECOMMENDATION_API_KEY`, `PORT`), recusando a partida com chave de serviço menor que 32 caracteres,, expondo a property `DATABASE_URL` já montada no formato de DSN do `psycopg2`.
- **Testes** (`tests/`), `test_postgres_client.py` cobre o pool e o context manager de cursor; `test_server.py` cobre as ferramentas, a autenticação (chaves aceitas, 401, 403, destino sem chaves, chave curta), `/health`, `/ready` e a versão usando `starlette.testclient.TestClient`; `test_recommendation_client.py` cobre o cliente da `api-recommendation` (campos, limite, cabeçalhos, erros).

```Tree do Repositório
├── .github/
│   ├── CODEOWNERS
│   ├── CONTRIBUTING.md
│   └── pull_request_template.md
├── tests/
│   ├── test_postgres_client.py
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
├── postgres_client.py
├── requirements.txt
├── server.py
└── settings.py
```
