from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

import server
from settings import settings


def test_listar_ofertas_de_placas_monta_query_certa():
    fake_cur = MagicMock()
    fake_cur.fetchall.return_value = [{"fornecedor": "ACME", "potencia_wp": 600}]

    with patch("server.get_cursor") as mock_get_cursor:
        mock_get_cursor.return_value.__enter__.return_value = fake_cur
        resultado = server.listar_ofertas_de_placas(potencia_minima_wp=500)

    assert resultado == [{"fornecedor": "ACME", "potencia_wp": 600}]
    fake_cur.execute.assert_called_once()
    params = fake_cur.execute.call_args[0][1]
    assert params["potencia_minima_wp"] == 500


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
