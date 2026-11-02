<p align="center">
  <img src="../assets/readme/banners/mcp.png" alt="MCP" width="100%">
</p>

# Situação

Leitura de 2026-11-02, depois de unificar `qa` e `main`.

- As seis ferramentas e a autenticação por chave de serviço estão implementadas.
- O catálogo é lido do `api-core` pelos endpoints `GET /internal/catalog/**`; o serviço não tem credencial de banco. O readiness depende do `/actuator/health` do `api-core`.
- A lista de hosts permitidos é fixa para local e QA. Hosts de produção podem exigir ajuste de configuração de transporte.
- Não há OpenAPI ou Swagger próprio. O catálogo MCP define os parâmetros.
