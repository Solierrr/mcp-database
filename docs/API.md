<p align="center">
  <img src="../assets/readme/banners/mcp.png" alt="MCP" width="100%">
</p>

# Protocolo de ferramentas

O transporte é o MCP Streamable HTTP em `/mcp`, com a `X-Service-Key` de um dos agentes autorizados, e o `x-api-key` continua aceito como alternativa legada quando `MCP_API_KEY` existe. O `/health` e o `/ready` são públicos.

| Ferramenta | Uso |
|---|---|
| `recomendar_ofertas` | Ofertas ordenadas por estratégia |
| `recomendar_profissionais` | Profissionais ordenados por estratégia e profissão |
| `recomendar_fornecedores` | Fornecedores, com contexto de unidade quando necessário |
| `listar_itens_de_fixacao` | Infraestrutura elegível por preço |
| `listar_profissoes` | Identificadores e nomes de profissões |
| `buscar_tecnicos_credenciados` | Técnicos por profissão e cidade |

Um cliente pode chamar `listar_profissoes` sem argumentos e usar o identificador retornado em `recomendar_profissionais`. Os limites das recomendações e itens de fixação são ajustados entre um e vinte. A busca de técnicos não tem esse limite no código.

O cliente de feeds usa timeout de quinze segundos e devolve `fonte`, `avisos` e `itens`. Falhas HTTP viram um objeto com `erro`, que o agente precisa avaliar. Erros de autenticação do transporte usam `application/problem+json` com 401 ou 403, conforme o [padrão](https://github.com/Solierrr/docs-warehouse/blob/main/docs/standards/ERRORS.md).
