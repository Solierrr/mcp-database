"""Servidor MCP que expõe o Postgres 'Negócio'."""

from typing import Literal

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from postgres_client import get_cursor
from recommendation_client import buscar_feed
from settings import settings

_LIMITE_MAXIMO = 20

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


class ExigirAPIKey(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.headers.get("x-api-key") != settings.MCP_API_KEY:
            return JSONResponse(
                {"erro": "API key ausente ou inválida"}, status_code=401
            )
        return await call_next(request)


app = mcp.streamable_http_app()
app.add_middleware(ExigirAPIKey)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
