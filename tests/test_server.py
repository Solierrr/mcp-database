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


def test_autenticacao_por_api_key():
    """Os 3 casos num teste só: StreamableHTTPSessionManager.run() só pode
    ser chamado uma vez por instância — TestClient(server.app) separado em
    cada teste quebraria a partir do segundo."""
    accept = {"Accept": "application/json, text/event-stream"}

    with TestClient(server.app) as client:
        sem_chave = client.post("/mcp", json={}, headers=accept)
        assert sem_chave.status_code == 401

        chave_errada = client.post(
            "/mcp", json={}, headers={**accept, "x-api-key": "errada"}
        )
        assert chave_errada.status_code == 401

        chave_certa = client.post(
            "/mcp", json={}, headers={**accept, "x-api-key": settings.MCP_API_KEY}
        )
        assert chave_certa.status_code != 401


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
