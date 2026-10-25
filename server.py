"""Servidor MCP que expõe o Postgres 'Negócio'."""

import asyncio
import hmac
import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Literal

import psycopg2
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

import postgres_client
from postgres_client import get_cursor
from recommendation_client import buscar_feed
from settings import settings
from version import VERSION

_LIMITE_MAXIMO = 20
_TIMEOUT_DO_PRONTO_SEGUNDOS = 2
_ROTAS_PUBLICAS = {"/health", "/ready"}
_CHAMADORES_DO_MCP = ("ai-assistant", "ai-operational")

logger = logging.getLogger("uvicorn.error")

mcp = FastMCP(
    "solaria-negocio",
    transport_security=TransportSecuritySettings(
        allowed_hosts=[
            "127.0.0.1:*",
            "localhost:*",
            "api-mcp-wey6.onrender.com",
        ],
        allowed_origins=[
            "http://127.0.0.1:*",
            "http://localhost:*",
            "https://api-mcp-wey6.onrender.com",
        ],
    ),
)


def _limitar(limite: int) -> int:
    return max(1, min(limite, _LIMITE_MAXIMO))


@mcp.tool()
async def recomendar_ofertas(
    estrategia: Literal[
        "best_value", "most_efficient", "nearest_available", "most_proven"
    ] = "best_value",
    unidade_id: str = "",
    limite: int = 10,
) -> dict:
    """Recomenda ofertas de placas solares já ranqueadas pela api-recommendation
    (top-N com a métrica e os motivos de cada posição). Estratégias:
    best_value (menor preço por Wp), most_efficient (maior eficiência),
    nearest_available (fornecedor mais próximo da unidade; exige unidade_id) e
    most_proven (mais presente em propostas aceitas). Cruze o resultado com as
    necessidades do usuário; não reordene nem invente ofertas."""
    return await buscar_feed(
        "offers",
        {"strategy": estrategia, "local_unit_id": unidade_id},
        _limitar(limite),
    )


@mcp.tool()
async def recomendar_profissionais(
    estrategia: Literal[
        "best_match", "top_rated", "most_qualified", "most_experienced", "most_reliable"
    ] = "best_match",
    profissao_id: str = "",
    limite: int = 10,
) -> dict:
    """Recomenda profissionais técnicos já ranqueados pela api-recommendation.
    Estratégias: best_match (equilíbrio geral), top_rated (melhor avaliação),
    most_qualified (mais certificações válidas), most_experienced (mais
    serviços concluídos) e most_reliable (menos cancelamentos). Para filtrar
    por profissão, use o id devolvido por listar_profissoes."""
    return await buscar_feed(
        "professionals",
        {"strategy": estrategia, "profession_id": profissao_id},
        _limitar(limite),
    )


@mcp.tool()
async def recomendar_fornecedores(
    estrategia: Literal["most_proven", "broadest_catalog", "nearest"] = "most_proven",
    unidade_id: str = "",
    limite: int = 10,
) -> dict:
    """Recomenda empresas fornecedoras já ranqueadas pela api-recommendation.
    Estratégias: most_proven (mais propostas aceitas), broadest_catalog (maior
    catálogo de ofertas) e nearest (mais próxima da unidade; exige
    unidade_id)."""
    return await buscar_feed(
        "suppliers",
        {"strategy": estrategia, "local_unit_id": unidade_id},
        _limitar(limite),
    )


@mcp.tool()
def listar_profissoes() -> list[dict]:
    """Lista as profissões cadastradas, com o id usado para filtrar
    recomendar_profissionais."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT id::text AS id, name AS nome FROM profession ORDER BY name;"
        )
        return cur.fetchall()


@mcp.tool()
def listar_itens_de_fixacao(
    tipo: Literal["", "RAIL", "CLAMP", "BRACKET", "HOOK", "KIT", "OTHER"] = "",
    marca: str = "",
    limite: int = 10,
) -> list[dict]:
    """Lista ofertas de itens de fixação e infraestrutura (trilho, grampo, suporte,
    gancho, kit), da mais barata para a mais cara. Não há ranking por mérito para esses
    itens: a ordem é só o preço. Filtra por tipo e/ou marca, se informado."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT
                comp.trade_name AS fornecedor,
                b.name AS marca,
                m.model AS modelo,
                m.infrastructure_type AS tipo,
                o.unit_price AS preco_unitario,
                o.availability AS disponibilidade,
                o.expiration_date AS validade
            FROM offer o
            JOIN supplier s ON s.id = o.fk_supplier
            JOIN company comp ON comp.id = s.fk_company
            JOIN model m ON m.id = o.fk_model
            JOIN brand b ON b.id = m.fk_brand
            WHERE m.product_type = 'INFRASTRUCTURE'
              AND s.status = 'ACTIVE'
              AND m.status = 'APPROVED'
              AND o.commercial_status = 'ACTIVE'
              AND o.availability > 0
              AND (o.expiration_date IS NULL OR o.expiration_date > now())
              AND (%(tipo)s = '' OR m.infrastructure_type = %(tipo)s)
              AND (%(marca)s = '' OR b.name ILIKE %(marca)s)
            ORDER BY o.unit_price ASC, o.id
            LIMIT %(limite)s;
            """,
            {
                "tipo": tipo,
                "marca": f"%{marca}%" if marca else "",
                "limite": _limitar(limite),
            },
        )
        return cur.fetchall()


@mcp.tool()
def buscar_tecnicos_credenciados(profissao: str = "", cidade: str = "") -> list[dict]:
    """Busca técnicos credenciados (afiliados a alguma empresa técnica),
    com sua profissão e registro. Filtra por nome da profissão e/ou
    cidade da empresa à qual está afiliado, se informado."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT
                p.name AS nome_tecnico,
                comp.trade_name AS empresa_afiliada,
                ta.affiliation_type AS tipo_afiliacao,
                prof.name AS profissao,
                pr.council AS conselho,
                pr.number AS numero_registro,
                pr.expiration_date AS validade_registro,
                addr.city AS cidade
            FROM technician t
            JOIN person p ON p.id = t.fk_person
            JOIN technician_affiliation ta ON ta.fk_technician = t.id
            JOIN company comp ON comp.id = ta.fk_company
            JOIN address addr ON addr.id = comp.fk_address
            LEFT JOIN professional_registration pr ON pr.fk_technician = t.id
            LEFT JOIN profession prof ON prof.id = pr.fk_profession
            WHERE (%(profissao)s = '' OR prof.name ILIKE %(profissao)s)
              AND (%(cidade)s = '' OR addr.city ILIKE %(cidade)s)
            ORDER BY p.name;
            """,
            {
                "profissao": f"%{profissao}%" if profissao else "",
                "cidade": f"%{cidade}%" if cidade else "",
            },
        )
        return cur.fetchall()


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "UP", "version": VERSION})


@mcp.custom_route("/ready", methods=["GET"])
async def ready(request: Request) -> JSONResponse:
    try:
        await asyncio.wait_for(
            asyncio.to_thread(postgres_client.ping, _TIMEOUT_DO_PRONTO_SEGUNDOS),
            timeout=_TIMEOUT_DO_PRONTO_SEGUNDOS + 1,
        )
    except (psycopg2.Error, OSError, TimeoutError):
        return JSONResponse({"status": "DOWN"}, status_code=503)
    return JSONResponse({"status": "UP"})


def _problema(request: Request, status: int, codigo: str, detalhe: str) -> JSONResponse:
    corpo = {
        "type": "about:blank",
        "title": codigo,
        "status": status,
        "errorCode": codigo,
        "detail": detalhe,
        "instance": request.url.path,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    return JSONResponse(
        corpo, status_code=status, media_type="application/problem+json"
    )


def _chamador(chave: str) -> str | None:
    for chamador, esperada in settings.service_keys.items():
        if hmac.compare_digest(chave.encode(), esperada.encode()):
            return chamador
    return None


def _chave_antiga_valida(chave: str | None) -> bool:
    return bool(
        chave
        and settings.MCP_API_KEY
        and hmac.compare_digest(chave.encode(), settings.MCP_API_KEY.encode())
    )


class ExigirChaveDeServico(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _ROTAS_PUBLICAS:
            return await call_next(request)
        chave = request.headers.get("x-service-key")
        if chave:
            chamador = _chamador(chave)
            if chamador in _CHAMADORES_DO_MCP:
                return await call_next(request)
            if chamador:
                return _problema(
                    request,
                    403,
                    "FORBIDDEN",
                    "Serviço chamador não autorizado nesta rota.",
                )
        elif _chave_antiga_valida(request.headers.get("x-api-key")):
            return await call_next(request)
        return _problema(
            request, 401, "UNAUTHENTICATED", "Chave de serviço ausente ou inválida."
        )


app = mcp.streamable_http_app()
app.add_middleware(ExigirChaveDeServico)
_executar_sessoes = app.router.lifespan_context


@asynccontextmanager
async def _ciclo_de_vida(app):
    logger.info("mcp-database %s iniciado", VERSION)
    async with _executar_sessoes(app):
        yield


app.router.lifespan_context = _ciclo_de_vida

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
