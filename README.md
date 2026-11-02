<p align="center">
  <img src="./assets/readme/banners/mcp.png" alt="MCP" width="100%">
</p>

<p align="center">
  <img src="./assets/readme/stacks/python.png" width="100" hspace="8" alt="Python" title="Python">
  <img src="./assets/readme/stacks/postgresql.png" width="100" hspace="8" alt="PostgreSQL" title="PostgreSQL">
</p>

# Ferramentas de consulta dos agentes

[![License](https://img.shields.io/github/license/Solierrr/mcp-database)](https://github.com/Solierrr/mcp-database/blob/main/LICENSE)
[![GitHub Last Commit](https://img.shields.io/github/last-commit/Solierrr/mcp-database)](https://github.com/Solierrr/mcp-database/commits)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/Solierrr/mcp-database)](https://github.com/Solierrr/mcp-database/pulls)
[![Release](https://img.shields.io/github/v/release/Solierrr/mcp-database)](https://github.com/Solierrr/mcp-database/releases)

Este serviço oferece aos assistentes ferramentas de consulta sobre ofertas, fornecedores, profissões e técnicos. Ele apresenta capacidades conhecidas para que o atendimento consulte os dados disponíveis e explique os resultados sem formular consultas livres. O serviço também recebe recomendações já ordenadas e preserva seus motivos e métricas.

O acesso usa um protocolo de ferramentas autenticado entre serviços. Parte das ferramentas consulta o PostgreSQL de negócio, e outra parte chama o motor de recomendações. O servidor transforma os resultados para o formato usado pelos assistentes. Ele não é dono do cadastro e não altera os dados de negócio.

## Aprofunde-se no Projeto!

- [OVERVIEW.md](./docs/OVERVIEW.md), finalidade e regras de produto.
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md), componentes, dados e integrações.
- [RUNNING.md](./docs/RUNNING.md), preparação e execução local.
- [API.md](./docs/API.md), autenticação e uso do contrato.
- [DEPLOY.md](./docs/DEPLOY.md), ambientes e publicação.
- [STATUS.md](./docs/STATUS.md), limites observados.
- [Fluxos](./flows/), etapas e casos de erro do repositório.
- [PENDENCIAS.md](./PENDENCIAS.md), questões para revisão.

## Contribuindo

- [CONTRIBUTING.md](https://github.com/Solierrr/.github/blob/main/.github/CONTRIBUTING.md), convenções de contribuição.
- [CODE_OF_CONDUCT.md](https://github.com/Solierrr/.github/blob/main/CODE_OF_CONDUCT.md), código de conduta.
- [SECURITY.md](https://github.com/Solierrr/.github/blob/main/SECURITY.md), relato de vulnerabilidades.
