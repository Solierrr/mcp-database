from unittest.mock import MagicMock

import postgres_client


def test_get_cursor_comita_em_sucesso(monkeypatch):
    fake_pool = MagicMock()
    fake_conn = MagicMock()
    fake_pool.getconn.return_value = fake_conn
    monkeypatch.setattr(postgres_client, "_get_pool", lambda: fake_pool)

    with postgres_client.get_cursor():
        pass

    fake_conn.commit.assert_called_once()
    fake_pool.putconn.assert_called_once_with(fake_conn)


def test_get_cursor_faz_rollback_e_devolve_conexao_em_erro(monkeypatch):
    fake_pool = MagicMock()
    fake_conn = MagicMock()
    fake_conn.cursor.return_value.__enter__.side_effect = ValueError("erro simulado")
    fake_pool.getconn.return_value = fake_conn
    monkeypatch.setattr(postgres_client, "_get_pool", lambda: fake_pool)

    try:
        with postgres_client.get_cursor():
            pass
        assert False, "deveria relançar a exceção"
    except ValueError:
        pass

    fake_conn.rollback.assert_called_once()
    fake_pool.putconn.assert_called_once_with(fake_conn)


def test_ping_usa_conexao_propria_com_timeout_e_fecha(monkeypatch):
    fake_conn = MagicMock()
    connect = MagicMock(return_value=fake_conn)
    monkeypatch.setattr(postgres_client.psycopg2, "connect", connect)

    postgres_client.ping(2)

    assert connect.call_args.kwargs == {"connect_timeout": 2}
    cursor = fake_conn.cursor.return_value.__enter__.return_value
    cursor.execute.assert_called_once_with("SELECT 1;")
    fake_conn.close.assert_called_once()
