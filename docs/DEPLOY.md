<p align="center">
  <img src="../assets/readme/banners/mcp.png" alt="MCP" width="100%">
</p>

# Deploy

O workflow declara QA em https://api-mcp-wey6.onrender.com e verificação de cluster de produção. O container usa Python 3.14 e porta 8001. Os processos comuns estão em [QA_RENDER.md](https://github.com/Solierrr/docs-warehouse/blob/main/readme/deploy/QA_RENDER.md) e [PROD_GKE_ARGOCD.md](https://github.com/Solierrr/docs-warehouse/blob/main/readme/deploy/PROD_GKE_ARGOCD.md).

A proteção de transporte aceita hosts locais e o host de QA declarados no código. Um novo host interno ou público precisa ser compatível com essa lista. O script de Render depende do executável Infisical disponível no caminho esperado.

O serviço está em operação no cluster de produção, com os Secrets, as variáveis e os privilégios de banco fornecidos pela infraestrutura.
