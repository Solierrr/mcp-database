<p align="center">
  <img src="../assets/readme/banners/mcp.png" alt="MCP" width="100%">
</p>

# Situação

Leitura da main em 2026-10-31.

- As seis ferramentas e a autenticação por chave de serviço estão implementadas.
- As consultas diretas ainda usam colunas `fk_*` e acesso a tabelas de negócio, e a documentação antiga aponta um schema e um papel de leitura que não existem mais no console atual, por isso a atualização para o schema atual do `api-core` está pendente.
- O servidor ainda exige PostgreSQL mesmo para ferramentas de recomendação.
- A lista de hosts permitidos é fixa para local e QA. Hosts de produção podem exigir ajuste de configuração de transporte.
- Não há OpenAPI ou Swagger próprio. O catálogo MCP define os parâmetros.
