# Rodando o Projeto Localmente

Este repositório é Python. O processo local é sempre o mesmo: clonar, criar um ambiente virtual, instalar as dependências do `requirements.txt` e subir a aplicação via `uvicorn`, apontando para o objeto ASGI `app` exposto em `server.py`. Antes de iniciar, verifique a seção de impedimentos abaixo — o serviço depende de um `api-core` acessível, da chave de serviço dele e de uma `MCP_API_KEY` configurada, mesmo em ambiente local.

<p>
  <a href="https://github.com/syvixor/skills-icons">
    <img src="https://skills.syvixor.com/api/icons?i=python,github" height="48" alt="Rodando o Projeto — api-mcp">
  </a>
</p>

## Possíveis Impedimentos

- **Python 3.12+ instalado localmente** {a confirmar: versão exata, não há `Dockerfile` no repositório para conferir a base image usada em produção}.
- **Acesso ao `api-core`**, as ferramentas `listar_profissoes`, `listar_itens_de_fixacao` e `buscar_tecnicos_credenciados` dependem de um `api-core` alcançável em `PERSISTENCE_BASE_URL` que exponha `/internal/catalog/**`, e de `SERVICE_KEY_CORE` com a chave de serviço do `mcp-database` — em produção essa chave vem do [Infisical](https://infisical.com). Sem o `api-core`, as ferramentas respondem `{"erro": ...}`.
- **`MCP_API_KEY` definida**, toda requisição ao endpoint `/mcp` passa pelo middleware `ExigirAPIKey` (`server.py`); sem o header `x-api-key` correto a aplicação sobe normalmente, mas todas as chamadas retornam `401`.
- **Secrets locais**, variáveis equivalentes às injetadas em runtime pelo Infisical precisam ser criadas manualmente em um `.env` local a partir do `.env.example` — sem elas, a aplicação falha ao iniciar (`pydantic-settings` valida os campos obrigatórios de `settings.py` na importação).

## Instalação do Projeto

### Iniciando o repositório com o Github

<p>
  <a href="https://github.com/syvixor/skills-icons">
    <img src="https://skills.syvixor.com/api/icons?i=github,vscode" height="48" alt="Frameworks">
  </a>
</p>

Clone o repositório e abra no VS Code.

```Comandos para clonar o repositório
git clone https://github.com/Solierrr/api-mcp.git
cd ./api-mcp
code . -r
```

### Configurando variáveis de ambiente

<p>
  <a href="https://github.com/syvixor/skills-icons">
    <img src="https://skills.syvixor.com/api/icons?i=python" height="48" alt="Frameworks">
  </a>
</p>

Copie o `.env.example` para `.env` e preencha com `PERSISTENCE_BASE_URL`, `SERVICE_KEY_CORE` e uma `MCP_API_KEY` própria (o valor não precisa ser o mesmo usado em produção, só precisa ser consistente entre quem sobe o servidor e quem chama a ferramenta MCP).

```Comandos para configurar o ambiente
copy .env.example .env
```

### Instalando dependências necessárias para rodar o projeto localmente

<p>
  <a href="https://github.com/syvixor/skills-icons">
    <img src="https://skills.syvixor.com/api/icons?i=python" height="48" alt="Frameworks">
  </a>
</p>

Crie um ambiente virtual antes de instalar as dependências, para não poluir o Python global da máquina. O servidor expõe o objeto ASGI `app` no módulo `server.py` (`app = mcp.streamable_http_app()`), então o `uvicorn` aponta para `server:app`.

```Comandos para instalação de dependências
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
```

Alternativamente, o próprio `server.py` sobe o Uvicorn quando executado diretamente (`if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=settings.PORT)`), lendo a porta de `settings.PORT` (padrão `8001`):

```Comando alternativo de start
python server.py
```

## Rodando os testes

<p>
  <a href="https://github.com/syvixor/skills-icons">
    <img src="https://skills.syvixor.com/api/icons?i=pytest,python" height="48" alt="Testes">
  </a>
</p>

Os testes usam `pytest` e `httpx`/`starlette.testclient` para simular chamadas ao app ASGI sem depender de um `api-core` real (o transporte HTTP é simulado).

```Comando para rodar os testes
pytest --cov
```
