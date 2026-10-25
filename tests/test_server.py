import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.testclient import TestClient

import server
from settings import settings


def test_recomendar_ofertas_repassa_estrategia_e_unidade():
    with patch("server.buscar_feed", new_callable=AsyncMock) as feed:
        feed.return_value = {"fonte": "graph", "avisos": [], "itens": []}
        resultado = asyncio.run(
            server.recomendar_ofertas(
                estrategia="nearest_available", unidade_id="u-1", limite=5
            )
        )

    assert resultado["fonte"] == "graph"
    feed.assert_awaited_once_with(
        "offers", {"strategy": "nearest_available", "local_unit_id": "u-1"}, 5
    )


def test_recomendar_profissionais_repassa_a_profissao():
    with patch("server.buscar_feed", new_callable=AsyncMock) as feed:
        feed.return_value = {"fonte": "graph", "avisos": [], "itens": []}
        asyncio.run(server.recomendar_profissionais(profissao_id="p-1"))

    feed.assert_awaited_once_with(
        "professionals", {"strategy": "best_match", "profession_id": "p-1"}, 10
    )


def test_recomendar_fornecedores_usa_a_estrategia_padrao():
    with patch("server.buscar_feed", new_callable=AsyncMock) as feed:
        feed.return_value = {"fonte": "fallback", "avisos": [], "itens": []}
        asyncio.run(server.recomendar_fornecedores())

    feed.assert_awaited_once_with(
        "suppliers", {"strategy": "most_proven", "local_unit_id": ""}, 10
    )


@pytest.mark.parametrize("pedido, esperado", [(0, 1), (-3, 1), (7, 7), (500, 20)])
def test_limite_fica_entre_1_e_o_maximo(pedido, esperado):
    assert server._limitar(pedido) == esperado


def test_listar_profissoes_consulta_a_tabela():
    fake_cur = MagicMock()
    fake_cur.fetchall.return_value = [{"id": "p-1", "nome": "Engenheiro"}]

    with patch("server.get_cursor") as mock_get_cursor:
        mock_get_cursor.return_value.__enter__.return_value = fake_cur
        resultado = server.listar_profissoes()

    assert resultado == [{"id": "p-1", "nome": "Engenheiro"}]
    assert "FROM profession" in fake_cur.execute.call_args[0][0]


def test_buscar_tecnicos_credenciados_filtra_por_profissao():
    fake_cur = MagicMock()
    fake_cur.fetchall.return_value = [{"nome_tecnico": "João Silva"}]

    with patch("server.get_cursor") as mock_get_cursor:
        mock_get_cursor.return_value.__enter__.return_value = fake_cur
        resultado = server.buscar_tecnicos_credenciados(profissao="eletric")

    assert resultado == [{"nome_tecnico": "João Silva"}]
    params = fake_cur.execute.call_args[0][1]
    assert params["profissao"] == "%eletric%"


ACCEPT = {"Accept": "application/json, text/event-stream"}


def test_chaves_aceitas_chegam_ao_mcp():
    """Os casos aceitos num teste só: StreamableHTTPSessionManager.run() só pode
    ser chamado uma vez por instância — TestClient(server.app) separado em
    cada teste quebraria a partir do segundo."""
    with TestClient(server.app) as client:
        for cabecalho in (
            {"X-Service-Key": settings.SERVICE_KEY_AI_ASSISTANT},
            {"X-Service-Key": settings.SERVICE_KEY_AI_OPERATIONAL},
            {"x-api-key": settings.MCP_API_KEY},
        ):
            resposta = client.post("/mcp", json={}, headers={**ACCEPT, **cabecalho})
            assert resposta.status_code not in (401, 403)


@pytest.mark.parametrize(
    "cabecalho",
    [
        {},
        {"X-Service-Key": "chave-errada-com-mais-de-32-caracteres"},
        {"x-api-key": "errada"},
        {"X-Service-Key": "chave-errada-com-mais-de-32-caracteres", "x-api-key": ""},
    ],
)
def test_chave_ausente_ou_invalida_responde_401_em_problem_detail(cabecalho):
    resposta = TestClient(server.app).post(
        "/mcp", json={}, headers={**ACCEPT, **cabecalho}
    )

    assert resposta.status_code == 401
    assert resposta.headers["content-type"] == "application/problem+json"
    corpo = resposta.json()
    assert corpo["errorCode"] == "UNAUTHENTICATED"
    assert corpo["status"] == 401
    assert corpo["instance"] == "/mcp"


def test_chave_invalida_nao_cai_para_a_chave_antiga():
    resposta = TestClient(server.app).post(
        "/mcp",
        json={},
        headers={
            **ACCEPT,
            "X-Service-Key": "chave-errada-com-mais-de-32-caracteres",
            "x-api-key": settings.MCP_API_KEY,
        },
    )

    assert resposta.status_code == 401


def test_sem_chave_antiga_configurada_x_api_key_e_recusada(monkeypatch):
    monkeypatch.setattr(settings, "MCP_API_KEY", None)

    resposta = TestClient(server.app).post(
        "/mcp", json={}, headers={**ACCEPT, "x-api-key": ""}
    )

    assert resposta.status_code == 401


def test_destino_sem_chaves_configuradas_recusa_tudo(monkeypatch):
    monkeypatch.setattr(settings, "MCP_API_KEY", None)
    monkeypatch.setattr(settings, "SERVICE_KEY_AI_ASSISTANT", None)
    monkeypatch.setattr(settings, "SERVICE_KEY_AI_OPERATIONAL", None)

    resposta = TestClient(server.app).post(
        "/mcp", json={}, headers={**ACCEPT, "X-Service-Key": ""}
    )

    assert resposta.status_code == 401


def test_chamador_valido_fora_da_rota_responde_403(monkeypatch):
    monkeypatch.setattr(server, "_CHAMADORES_DO_MCP", ("ai-assistant",))

    resposta = TestClient(server.app).post(
        "/mcp",
        json={},
        headers={**ACCEPT, "X-Service-Key": settings.SERVICE_KEY_AI_OPERATIONAL},
    )

    assert resposta.status_code == 403
    assert resposta.json()["errorCode"] == "FORBIDDEN"


def test_chave_de_servico_curta_impede_a_partida():
    from pydantic import ValidationError

    from settings import Settings

    with pytest.raises(ValidationError):
        Settings(SERVICE_KEY_AI_ASSISTANT="curta")


def test_listar_itens_de_fixacao_filtra_tipo_marca_e_limite():
    fake_cur = MagicMock()
    fake_cur.fetchall.return_value = [{"fornecedor": "ACME", "tipo": "RAIL"}]

    with patch("server.get_cursor") as mock_get_cursor:
        mock_get_cursor.return_value.__enter__.return_value = fake_cur
        resultado = server.listar_itens_de_fixacao(tipo="RAIL", marca="alu", limite=500)

    assert resultado == [{"fornecedor": "ACME", "tipo": "RAIL"}]
    sql, params = fake_cur.execute.call_args[0]
    assert "product_type = 'INFRASTRUCTURE'" in sql
    assert params == {"tipo": "RAIL", "marca": "%alu%", "limite": 20}


def test_listar_itens_de_fixacao_sem_filtros_nao_restringe():
    fake_cur = MagicMock()
    fake_cur.fetchall.return_value = []

    with patch("server.get_cursor") as mock_get_cursor:
        mock_get_cursor.return_value.__enter__.return_value = fake_cur
        server.listar_itens_de_fixacao()

    params = fake_cur.execute.call_args[0][1]
    assert params == {"tipo": "", "marca": "", "limite": 10}


def test_versao_vem_do_version_txt():
    from pathlib import Path

    from version import VERSION

    assert VERSION == Path("version.txt").read_text(encoding="utf-8").strip()
    assert VERSION


def test_health_responde_vivo_com_a_versao_sem_chave():
    from version import VERSION

    resposta = TestClient(server.app).get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "UP", "version": VERSION}


def test_ready_responde_up_quando_o_banco_responde():
    with patch("server.postgres_client.ping") as ping:
        resposta = TestClient(server.app).get("/ready")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "UP"}
    ping.assert_called_once_with(2)


def test_ready_responde_down_sem_detalhes_quando_o_banco_falha():
    with patch("server.postgres_client.ping", side_effect=OSError("sem banco")):
        resposta = TestClient(server.app).get("/ready")

    assert resposta.status_code == 503
    assert resposta.json() == {"status": "DOWN"}


def test_ready_responde_down_quando_o_banco_nao_responde_a_tempo():
    with patch("server.postgres_client.ping", side_effect=TimeoutError):
        resposta = TestClient(server.app).get("/ready")

    assert resposta.status_code == 503
    assert resposta.json() == {"status": "DOWN"}
