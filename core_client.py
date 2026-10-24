import httpx

from settings import settings

_TIMEOUT_SEGUNDOS = 15.0
_transport: httpx.AsyncBaseTransport | None = None


def _cabecalhos() -> dict[str, str]:
    return {"X-Service-Key": settings.SERVICE_KEY_CORE}


def _profissao(item: dict) -> dict:
    return {"id": item["id"], "nome": item["name"]}


def _item_de_fixacao(item: dict) -> dict:
    return {
        "fornecedor": item["supplierTradeName"],
        "marca": item["brand"],
        "modelo": item["model"],
        "tipo": item["infrastructureType"],
        "preco_unitario": item["unitPrice"],
        "disponibilidade": item["availability"],
        "validade": item.get("expirationDate"),
    }


def _tecnico(item: dict) -> dict:
    return {
        "nome_tecnico": item["technicianName"],
        "empresa_afiliada": item["affiliatedCompany"],
        "tipo_afiliacao": item["affiliationType"],
        "profissao": item.get("profession"),
        "conselho": item.get("council"),
        "numero_registro": item.get("registrationNumber"),
        "validade_registro": item.get("registrationExpirationDate"),
        "cidade": item["city"],
    }


_CATALOGOS = {
    "professions": _profissao,
    "infrastructure-offers": _item_de_fixacao,
    "accredited-technicians": _tecnico,
}


async def buscar_catalogo(
    recurso: str, params: dict[str, str | int]
) -> list[dict] | dict:
    consulta = {nome: valor for nome, valor in params.items() if valor != ""}
    try:
        async with httpx.AsyncClient(
            base_url=settings.PERSISTENCE_BASE_URL,
            timeout=_TIMEOUT_SEGUNDOS,
            transport=_transport,
        ) as client:
            resposta = await client.get(
                f"/internal/catalog/{recurso}", params=consulta, headers=_cabecalhos()
            )
            resposta.raise_for_status()
            corpo = resposta.json()
    except httpx.HTTPStatusError as erro:
        return {"erro": _mensagem_de_erro(erro.response)}
    except (httpx.HTTPError, ValueError):
        return {"erro": "O serviço de dados está indisponível no momento."}

    converter = _CATALOGOS[recurso]
    return [converter(item) for item in corpo]


def _mensagem_de_erro(resposta: httpx.Response) -> str:
    try:
        detalhe = resposta.json().get("detail")
    except (ValueError, AttributeError):
        detalhe = None
    if isinstance(detalhe, str) and detalhe:
        return detalhe
    return f"O serviço de dados respondeu com erro {resposta.status_code}."
