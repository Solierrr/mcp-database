<p align="center">
  <img src="../assets/readme/banners/mcp.png" alt="MCP" width="100%">
</p>

# Arquitetura

O [server.py](https://github.com/Solierrr/mcp-database/blob/main/server.py) registra ferramentas no FastMCP e as serve por Starlette e Uvicorn. Não é uma API REST FastAPI.

```mermaid
flowchart LR
 A[ai-assistant e ai-operational] -->|MCP HTTP e X-Service-Key| M[FastMCP]
 M --> P[postgres_client.py]
 P --> D[(PostgreSQL de negócio)]
 M --> R[recommendation_client.py]
 R -->|HTTP e X-Service-Key| F[api-recommendation]
```

| Arquivo | Papel |
|---|---|
| `server.py` | Ferramentas, middleware e health |
| `settings.py` | Variáveis e validação de chaves |
| `postgres_client.py` | Pool síncrono de até dez conexões |
| `recommendation_client.py` | HTTP de feeds e conversão para os agentes |

A chave recebida identifica `ai-assistant` ou `ai-operational`. A chave própria `SERVICE_KEY` identifica este servidor na chamada ao motor de recomendações. A comparação usa tempo constante. A chave legada continua aceita apenas quando configurada e sem uma chave nova no cabeçalho.

As consultas SQL são parametrizadas, mas o código não impõe uma sessão SQL somente leitura, por isso o privilégio do login faz parte da configuração de acesso. O readiness abre uma conexão separada do pool e executa `SELECT 1`, a versão vem de `version.txt` e o serviço não tem schema próprio, com o fluxo completo descrito em [ASSISTANT_CHAT.md](https://github.com/Solierrr/docs-warehouse/blob/main/docs/flows/ASSISTANT_CHAT.md).