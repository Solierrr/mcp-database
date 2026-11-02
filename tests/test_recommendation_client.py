import asyncio

import httpx
import pytest

import recommendation_client
from settings import settings

OFERTA = {
    "rank": 1,
    "offer_id": "o1",
    "supplier_id": "s1",
    "supplier_trade_name": "ACME Solar",
    "model_id": "m1",
    "brand": "Marca",
    "model": "M-550",
    "power_wp": 550.0,
    "efficiency": 21.5,
    "unit_price": 900.0,
    "effective_availability": 40,
    "dimension": 2.5,
    "weight": 28.0,
    "accepted_proposal_quantity": 3,
    "distance_km": None,
    "ranking_value": 1.63,
    "ranking_unit": "BRL_per_Wp",
    "reasons": ["Preço efetivo de R$ 1.63 por Wp"],
}


@pytest.fixture
def servidor(monkeypatch):
    """Instala um transporte falso e devolve a lista de requisições feitas."""
    requisicoes = []

    def instalar(handler):
        def interno(request: httpx.Request) -> httpx.Response:
            requisicoes.append(request)
            return handler(request)

        monkeypatch.setattr(
            recommendation_client, "_transport", httpx.MockTransport(interno)
        )
        return requisicoes

    return instalar


def test_oferta_e_reduzida_aos_campos_do_agente(servidor):
    requisicoes = servidor(
        lambda r: httpx.Response(
            200, json={"source": "graph", "items": [OFERTA], "warnings": ["aviso"]}
        )
    )

    resultado = asyncio.run(
        recommendation_client.buscar_feed(
            "offers", {"strategy": "best_value", "local_unit_id": ""}, 10
        )
    )

    assert resultado["fonte"] == "graph"
    assert resultado["avisos"] == ["aviso"]
    assert resultado["itens"][0] == {
        "posicao": 1,
        "valor_do_ranking": 1.63,
        "unidade_do_ranking": "BRL_per_Wp",
        "motivos": ["Preço efetivo de R$ 1.63 por Wp"],
        "oferta_id": "o1",
        "fornecedor_id": "s1",
        "fornecedor": "ACME Solar",
        "marca": "Marca",
        "modelo": "M-550",
        "potencia_wp": 550.0,
        "eficiencia_pct": 21.5,
        "preco_unitario": 900.0,
        "disponibilidade": 40,
        "distancia_km": None,
    }
    assert requisicoes[0].url.path == "/feeds/offers"
    assert requisicoes[0].url.params["strategy"] == "best_value"
    assert "local_unit_id" not in requisicoes[0].url.params


def test_limite_corta_a_lista(servidor):
    servidor(
        lambda r: httpx.Response(
            200, json={"source": "graph", "items": [OFERTA] * 5, "warnings": []}
        )
    )

    resultado = asyncio.run(recommendation_client.buscar_feed("offers", {}, 2))

    assert len(resultado["itens"]) == 2


@pytest.mark.parametrize(
    "chave_de_servico, chave_antiga, esperado",
    [
        (
            "chave-de-servico-do-mcp-database-01",
            None,
            {"X-Service-Key": "chave-de-servico-do-mcp-database-01"},
        ),
        (
            "chave-de-servico-do-mcp-database-01",
            "chave-antiga",
            {
                "X-Service-Key": "chave-de-servico-do-mcp-database-01",
                "X-Recommendation-Key": "chave-antiga",
            },
        ),
        (None, "chave-antiga", {"X-Recommendation-Key": "chave-antiga"}),
        (None, None, {}),
    ],
)
def test_envia_as_chaves_configuradas(
    servidor, monkeypatch, chave_de_servico, chave_antiga, esperado
):
    monkeypatch.setattr(settings, "SERVICE_KEY", chave_de_servico)
    monkeypatch.setattr(settings, "RECOMMENDATION_API_KEY", chave_antiga)
    requisicoes = servidor(
        lambda r: httpx.Response(
            200, json={"source": "graph", "items": [], "warnings": []}
        )
    )

    asyncio.run(recommendation_client.buscar_feed("offers", {}, 10))

    enviados = {
        nome: requisicoes[0].headers[nome]
        for nome in ("X-Service-Key", "X-Recommendation-Key")
        if nome in requisicoes[0].headers
    }
    assert enviados == esperado


def test_erro_da_api_vira_mensagem_para_o_agente(servidor):
    servidor(
        lambda r: httpx.Response(
            422,
            json={
                "detail": {
                    "code": "LOCAL_UNIT_REQUIRED",
                    "message": "A estratégia nearest_available exige o parâmetro local_unit_id.",
                }
            },
        )
    )

    resultado = asyncio.run(
        recommendation_client.buscar_feed(
            "offers", {"strategy": "nearest_available"}, 10
        )
    )

    assert resultado == {
        "erro": "A estratégia nearest_available exige o parâmetro local_unit_id."
    }


def test_erro_sem_detalhe_usa_mensagem_generica(servidor):
    servidor(lambda r: httpx.Response(500, json={"detail": [{"msg": "x"}]}))

    resultado = asyncio.run(recommendation_client.buscar_feed("offers", {}, 10))

    assert resultado == {"erro": "A recomendação respondeu com erro 500."}


def test_servico_fora_do_ar_nao_derruba_a_ferramenta(servidor):
    def falha(request):
        raise httpx.ConnectError("sem conexão")

    servidor(falha)

    resultado = asyncio.run(recommendation_client.buscar_feed("professionals", {}, 10))

    assert resultado == {
        "erro": "O serviço de recomendação está indisponível no momento."
    }


def test_profissional_e_fornecedor_sao_reduzidos(servidor):
    profissional = {
        "rank": 1,
        "technician_id": "t1",
        "name": "Ana",
        "professions": ["Engenheira"],
        "average_rating_global": 4.8,
        "review_count_global": 12,
        "completed_service_count_global": 30,
        "certification_names": ["NR10"],
        "assigned_service_count_global": 31,
        "canceled_service_count_global": 1,
        "valid_certification_count": 1,
        "ranking_value": 0.9,
        "ranking_unit": "best_match_score_0_1",
        "reasons": ["motivo"],
    }
    fornecedor = {
        "rank": 1,
        "supplier_id": "s1",
        "company_id": "c1",
        "trade_name": "ACME",
        "business_type": "DISTRIBUIDOR",
        "offer_count": 4,
        "accepted_proposal_quantity": 9,
        "distance_km": 12.5,
        "ranking_value": 9.0,
        "ranking_unit": "accepted_proposal_quantity",
        "reasons": ["motivo"],
    }
    servidor(
        lambda r: httpx.Response(
            200,
            json={
                "source": "fallback",
                "items": [
                    profissional if "professionals" in r.url.path else fornecedor
                ],
            },
        )
    )

    profissionais = asyncio.run(
        recommendation_client.buscar_feed("professionals", {}, 5)
    )
    fornecedores = asyncio.run(recommendation_client.buscar_feed("suppliers", {}, 5))

    assert profissionais["itens"][0]["nome"] == "Ana"
    assert profissionais["itens"][0]["certificacoes"] == ["NR10"]
    assert "avisos" in profissionais and profissionais["avisos"] == []
    assert fornecedores["itens"][0]["nome"] == "ACME"
    assert fornecedores["itens"][0]["distancia_km"] == 12.5
