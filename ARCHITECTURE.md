# Arquitetura do Repositório

O `api-mcp` segue uma arquitetura enxuta de três camadas dentro de um único processo Python: um servidor MCP (`server.py`) que registra ferramentas invocáveis por um agente de IA, uma camada de acesso a dados (`postgres_client.py`) que isola o pool de conexões com o Postgres "Negócio", e uma camada de configuração (`settings.py`) que centraliza a leitura de variáveis de ambiente via `pydantic-settings`. O servidor é montado como uma aplicação ASGI (`mcp.streamable_http_app()`) servida pelo Uvicorn, com um middleware Starlette de autenticação por API key protegendo o único endpoint HTTP exposto (`/mcp`). Não há camada de roteamento REST tradicional: a superfície pública do serviço é o conjunto de ferramentas MCP registradas, descobertas dinamicamente pelo cliente (o `ai-assistant`) via protocolo MCP, e não por URLs fixas documentadas em um contrato OpenAPI.

<p>
  <a href="https://github.com/syvixor/skills-icons">
    <img src="https://skills.syvixor.com/api/icons?i=python,postgres,fastapi" height="48" alt="Arquitetura do api-mcp">
  </a>
</p>

- **Arquitetura seguida**, servidor MCP single-process sobre Starlette/Uvicorn, com ferramentas registradas via decorator (`@mcp.tool()`) em vez de rotas HTTP tradicionais — o transporte é o protocolo MCP (`streamable_http_app`), não REST.
- **Ferramentas MCP expostas** (`server.py`), duas ferramentas registradas hoje via `@mcp.tool()`:
  - `listar_ofertas_de_placas(potencia_minima_wp: float = 0, marca: str = "")`, consulta o Postgres "Negócio" e retorna ofertas de placas solares (fornecedor, marca, modelo, potência, eficiência, preço, disponibilidade e validade), filtrando por potência mínima em Wp e/ou marca, restrita a fornecedores `ACTIVE` e modelos `APPROVED`.
  - `buscar_tecnicos_credenciados(profissao: str = "", cidade: str = "")`, consulta técnicos credenciados afiliados a empresas técnicas, retornando nome, empresa afiliada, tipo de afiliação, profissão, conselho e registro profissional, filtrando por profissão e/ou cidade da empresa afiliada.
- **Camada de acesso ao Postgres** (`postgres_client.py`), um `psycopg2.pool.ThreadedConnectionPool` (1 a 10 conexões) instanciado sob demanda (lazy, em `_get_pool()`) e reaproveitado entre chamadas; o context manager `get_cursor()` entrega um cursor `RealDictCursor` (linhas como `dict`), faz `commit()` em caso de sucesso e `rollback()` em caso de exceção, sempre devolvendo a conexão ao pool no `finally`.
- **Middleware de autenticação** (`server.py`, classe `ExigirAPIKey`), um `BaseHTTPMiddleware` do Starlette que intercepta toda requisição ao app ASGI e retorna `401` com `{"erro": "API key ausente ou inválida"}` caso o header `x-api-key` não corresponda a `settings.MCP_API_KEY` — aplicado globalmente via `app.add_middleware(ExigirAPIKey)`, cobrindo o endpoint `/mcp` inteiro antes de qualquer ferramenta ser executada.
- **Configuração centralizada** (`settings.py`), classe `Settings(BaseSettings)` do `pydantic-settings` que lê `.env` e variáveis de ambiente (`DB_POSTGRES_HOST`, `DB_POSTGRES_PORT`, `DB_POSTGRES_USER`, `DB_POSTGRES_PASSWORD`, `DB_POSTGRES_BUSINESS`, `MCP_API_KEY`, `PORT`), expondo a property `DATABASE_URL` já montada no formato de DSN do `psycopg2`.
- **Testes** (`tests/`), `test_postgres_client.py` cobre o pool e o context manager de cursor; `test_server.py` cobre a montagem das queries das duas ferramentas e os três cenários de autenticação (sem chave, chave errada, chave certa) usando `starlette.testclient.TestClient`.

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
