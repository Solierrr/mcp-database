import asyncio

import httpx
import pytest

import core_client
from settings import settings

PROFISSAO = {"id": "p-1", "name": "Eletricista"}

OFERTA_DE_FIXACAO = {
    "offerId": "o-1",
    "supplierTradeName": "Solar Sul",
    "brand": "K2",
    "model": "Trilho 4,2 m",
    "infrastructureType": "RAIL",
    "unitPrice": "89.90",
    "availability": 120,
    "expirationDate": "2026-12-31T23:59:59-03:00",
}

TECNICO = {
    "technicianName": "Ana Souza",
    "affiliatedCompany": "Instala Mais",
    "affiliationType": "AFFILIATED",
    "profession": "Engenheiro eletricista",
    "council": "CREA-SP",
    "registrationNumber": "123456",
    "registrationExpirationDate": "2027-03-01T00:00:00",
    "city": "Campinas",
}


@pytest.fixture
def servidor(monkeypatch):
    requisicoes = []

    def instalar(handler):
        def interno(request: httpx.Request) -> httpx.Response:
            requisicoes.append(request)
            return handler(request)

        monkeypatch.setattr(core_client, "_transport", httpx.MockTransport(interno))
        return requisicoes

    return instalar


def test_profissoes_sao_reduzidas_a_id_e_nome(servidor):
    requisicoes = servidor(lambda r: httpx.Response(200, json=[PROFISSAO]))

    resultado = asyncio.run(core_client.buscar_catalogo("professions", {}))

    assert resultado == [{"id": "p-1", "nome": "Eletricista"}]
    assert requisicoes[0].url.path == "/internal/catalog/professions"
    assert requisicoes[0].method == "GET"


def test_itens_de_fixacao_mantem_os_campos_de_saida(servidor):
    servidor(lambda r: httpx.Response(200, json=[OFERTA_DE_FIXACAO]))

    resultado = asyncio.run(
        core_client.buscar_catalogo("infrastructure-offers", {"limit": 10})
    )

    assert resultado == [
        {
            "fornecedor": "Solar Sul",
            "marca": "K2",
            "modelo": "Trilho 4,2 m",
            "tipo": "RAIL",
            "preco_unitario": "89.90",
            "disponibilidade": 120,
            "validade": "2026-12-31T23:59:59-03:00",
        }
    ]


def test_item_de_fixacao_sem_validade_devolve_nulo(servidor):
    oferta = {**OFERTA_DE_FIXACAO, "expirationDate": None}
    servidor(lambda r: httpx.Response(200, json=[oferta]))

    resultado = asyncio.run(core_client.buscar_catalogo("infrastructure-offers", {}))

    assert resultado[0]["validade"] is None


def test_tecnicos_mantem_os_campos_de_saida(servidor):
    servidor(lambda r: httpx.Response(200, json=[TECNICO]))

    resultado = asyncio.run(core_client.buscar_catalogo("accredited-technicians", {}))

    assert resultado == [
        {
            "nome_tecnico": "Ana Souza",
            "empresa_afiliada": "Instala Mais",
            "tipo_afiliacao": "AFFILIATED",
            "profissao": "Engenheiro eletricista",
            "conselho": "CREA-SP",
            "numero_registro": "123456",
            "validade_registro": "2027-03-01T00:00:00",
            "cidade": "Campinas",
        }
    ]


def test_tecnico_sem_registro_nem_profissao_aceita_nulos(servidor):
    tecnico = {
        "technicianName": "Bruno Lima",
        "affiliatedCompany": "Instala Mais",
        "affiliationType": "AFFILIATED",
        "profession": None,
        "council": None,
        "registrationNumber": None,
        "registrationExpirationDate": None,
        "city": "Campinas",
    }
    servidor(lambda r: httpx.Response(200, json=[tecnico]))

    resultado = asyncio.run(core_client.buscar_catalogo("accredited-technicians", {}))

    assert resultado[0]["nome_tecnico"] == "Bruno Lima"
    assert resultado[0]["profissao"] is None
    assert resultado[0]["conselho"] is None
    assert resultado[0]["numero_registro"] is None
    assert resultado[0]["validade_registro"] is None


def test_resposta_vazia_devolve_lista_vazia(servidor):
    servidor(lambda r: httpx.Response(200, json=[]))

    resultado = asyncio.run(core_client.buscar_catalogo("professions", {}))

    assert resultado == []


def test_envia_a_chave_de_servico(servidor, monkeypatch):
    monkeypatch.setattr(settings, "SERVICE_KEY_CORE", "chave-de-teste")
    requisicoes = servidor(lambda r: httpx.Response(200, json=[]))

    asyncio.run(core_client.buscar_catalogo("professions", {}))

    assert requisicoes[0].headers["X-Service-Key"] == "chave-de-teste"


def test_usa_a_url_base_configurada(servidor, monkeypatch):
    monkeypatch.setattr(settings, "PERSISTENCE_BASE_URL", "http://core.interno:8080")
    requisicoes = servidor(lambda r: httpx.Response(200, json=[]))

    asyncio.run(core_client.buscar_catalogo("professions", {}))

    assert (
        str(requisicoes[0].url)
        == "http://core.interno:8080/internal/catalog/professions"
    )


def test_filtros_vazios_nao_vao_na_consulta(servidor):
    requisicoes = servidor(lambda r: httpx.Response(200, json=[]))

    asyncio.run(
        core_client.buscar_catalogo(
            "infrastructure-offers",
            {"infrastructureType": "", "brand": "k2", "limit": 5},
        )
    )

    params = requisicoes[0].url.params
    assert "infrastructureType" not in params
    assert params["brand"] == "k2"
    assert params["limit"] == "5"


@pytest.mark.parametrize("status", [401, 403])
def test_chave_recusada_vira_mensagem_para_o_agente(servidor, status):
    servidor(
        lambda r: httpx.Response(
            status,
            json={
                "title": "UNAUTHORIZED",
                "status": status,
                "detail": "Chave inválida",
            },
        )
    )

    resultado = asyncio.run(core_client.buscar_catalogo("professions", {}))

    assert resultado == {"erro": "Chave inválida"}


def test_erro_sem_detalhe_usa_mensagem_generica(servidor):
    servidor(lambda r: httpx.Response(500, json={"status": 500}))

    resultado = asyncio.run(core_client.buscar_catalogo("professions", {}))

    assert resultado == {"erro": "O serviço de dados respondeu com erro 500."}


def test_erro_com_corpo_que_nao_e_json_usa_mensagem_generica(servidor):
    servidor(lambda r: httpx.Response(502, text="bad gateway"))

    resultado = asyncio.run(core_client.buscar_catalogo("professions", {}))

    assert resultado == {"erro": "O serviço de dados respondeu com erro 502."}


def test_servico_fora_do_ar_nao_derruba_a_ferramenta(servidor):
    def falha(request):
        raise httpx.ConnectError("sem conexão")

    servidor(falha)

    resultado = asyncio.run(core_client.buscar_catalogo("professions", {}))

    assert resultado == {"erro": "O serviço de dados está indisponível no momento."}


def test_timeout_nao_derruba_a_ferramenta(servidor):
    def demora(request):
        raise httpx.ReadTimeout("lento")

    servidor(demora)

    resultado = asyncio.run(core_client.buscar_catalogo("accredited-technicians", {}))

    assert resultado == {"erro": "O serviço de dados está indisponível no momento."}


def test_resposta_com_corpo_invalido_vira_erro(servidor):
    servidor(lambda r: httpx.Response(200, text="<html>"))

    resultado = asyncio.run(core_client.buscar_catalogo("professions", {}))

    assert resultado == {"erro": "O serviço de dados está indisponível no momento."}
