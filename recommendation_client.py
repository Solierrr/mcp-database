"""Cliente HTTP da api-recommendation: busca o top-N ranqueado de um feed e
devolve só os campos úteis ao agente, em português."""

import httpx

from settings import settings

_TIMEOUT_SEGUNDOS = 15.0
_transport: httpx.AsyncBaseTransport | None = None


def _cabecalhos() -> dict[str, str]:
    if settings.RECOMMENDATION_API_KEY:
        return {"X-Recommendation-Key": settings.RECOMMENDATION_API_KEY}
    return {}


def _ranking(item: dict) -> dict:
    return {
        "posicao": item["rank"],
        "valor_do_ranking": item["ranking_value"],
        "unidade_do_ranking": item["ranking_unit"],
        "motivos": item["reasons"],
    }


def _oferta(item: dict) -> dict:
    return {
        **_ranking(item),
        "oferta_id": item["offer_id"],
        "fornecedor_id": item["supplier_id"],
        "fornecedor": item["supplier_trade_name"],
        "marca": item["brand"],
        "modelo": item["model"],
        "potencia_wp": item["power_wp"],
        "eficiencia_pct": item["efficiency"],
        "preco_unitario": item["unit_price"],
        "disponibilidade": item["effective_availability"],
        "distancia_km": item.get("distance_km"),
    }


def _profissional(item: dict) -> dict:
    return {
        **_ranking(item),
        "tecnico_id": item["technician_id"],
        "nome": item["name"],
        "profissoes": item["professions"],
        "nota_media": item["average_rating_global"],
        "avaliacoes": item["review_count_global"],
        "servicos_concluidos": item["completed_service_count_global"],
        "certificacoes": item["certification_names"],
    }


def _fornecedor(item: dict) -> dict:
    return {
        **_ranking(item),
        "fornecedor_id": item["supplier_id"],
        "empresa_id": item["company_id"],
        "nome": item["trade_name"],
        "tipo_de_negocio": item["business_type"],
        "quantidade_de_ofertas": item["offer_count"],
        "propostas_aceitas": item["accepted_proposal_quantity"],
        "distancia_km": item.get("distance_km"),
    }


_FEEDS = {
    "offers": _oferta,
    "professionals": _profissional,
    "suppliers": _fornecedor,
}


async def buscar_feed(feed: str, params: dict[str, str], limite: int) -> dict:
    """Consulta /feeds/{feed} e devolve `fonte`, `avisos` e os `itens` já
    reduzidos aos campos do agente. Falhas viram um dict com `erro`, para o
    agente explicar ao usuário em vez de a chamada da ferramenta quebrar."""
    consulta = {nome: valor for nome, valor in params.items() if valor}
    try:
        async with httpx.AsyncClient(
            base_url=settings.RECOMMENDATION_API_URL,
            timeout=_TIMEOUT_SEGUNDOS,
            transport=_transport,
        ) as client:
            resposta = await client.get(
                f"/feeds/{feed}", params=consulta, headers=_cabecalhos()
            )
            resposta.raise_for_status()
            corpo = resposta.json()
    except httpx.HTTPStatusError as erro:
        return {"erro": _mensagem_de_erro(erro.response)}
    except httpx.HTTPError:
        return {"erro": "O serviço de recomendação está indisponível no momento."}

    converter = _FEEDS[feed]
    itens = [converter(item) for item in corpo["items"][:limite]]
    return {
        "fonte": corpo["source"],
        "avisos": corpo.get("warnings", []),
        "itens": itens,
    }


def _mensagem_de_erro(resposta: httpx.Response) -> str:
    try:
        detalhe = resposta.json().get("detail")
    except ValueError:
        detalhe = None
    if isinstance(detalhe, dict):
        detalhe = detalhe.get("message")
    if isinstance(detalhe, str) and detalhe:
        return detalhe
    return f"A recomendação respondeu com erro {resposta.status_code}."
