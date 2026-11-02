<p align="center">
  <img src="../assets/readme/banners/mcp.png" alt="MCP" width="100%">
</p>

# Arquitetura

O [server.py](https://github.com/Solierrr/mcp-database/blob/main/server.py) registra ferramentas no FastMCP e as serve por Starlette e Uvicorn. Não é uma API REST FastAPI.

```mermaid
flowchart LR
 A[ai-assistant e ai-operational] -->|MCP HTTP e X-Service-Key| M[FastMCP]
 M --> C[core_client.py]
 C -->|HTTP e X-Service-Key| K[api-core]
 M --> R[recommendation_client.py]
 R -->|HTTP e X-Service-Key| F[api-recommendation]
```

| Arquivo | Papel |
|---|---|
| `server.py` | Ferramentas, middleware e health |
| `settings.py` | Variáveis e validação de chaves |
| `core_client.py` | HTTP do catálogo no `api-core` e conversão para os agentes |
| `recommendation_client.py` | HTTP de feeds e conversão para os agentes |

A chave recebida identifica `ai-assistant` ou `ai-operational`. A chave própria `SERVICE_KEY` identifica este servidor na chamada ao motor de recomendações. A comparação usa tempo constante. A chave legada continua aceita apenas quando configurada e sem uma chave nova no cabeçalho.

O servidor não acessa banco: o catálogo vem do `api-core` pelos endpoints internos `GET /internal/catalog/**`, só de leitura e protegidos pela chave de serviço. O readiness consulta `/actuator/health` do `api-core` com limite de dois segundos, a versão vem de `version.txt` e o serviço não tem schema próprio, com o fluxo completo descrito em [ASSISTANT_CHAT.md](https://github.com/Solierrr/docs-warehouse/blob/main/docs/flows/ASSISTANT_CHAT.md).