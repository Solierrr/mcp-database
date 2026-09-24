"""Servidor MCP que expõe o Postgres 'Negócio'."""

import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from postgres_client import get_cursor
from settings import settings

mcp = FastMCP("solaria-negocio")


@mcp.tool()
def listar_ofertas_de_placas(
    potencia_minima_wp: float = 0, marca: str = ""
) -> list[dict]:
    """Lista ofertas de placas solares disponíveis, com fornecedor, preço e
    potência. Filtra por potência mínima em Wp e/ou marca, se informado."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT
                comp.trade_name AS fornecedor,
                m.brand AS marca,
                m.model AS modelo,
                m.power_wp AS potencia_wp,
                m.efficiency AS eficiencia_pct,
                o.unit_price AS preco_unitario,
                o.availability AS disponibilidade,
                o.expiration_date AS validade
            FROM offer o
            JOIN supplier s ON s.id = o.fk_supplier
            JOIN company comp ON comp.id = s.fk_company
            JOIN model m ON m.id = o.fk_model
            WHERE s.status = 'ACTIVE'
              AND m.status = 'APPROVED'
              AND m.power_wp >= %(potencia_minima_wp)s
              AND (%(marca)s = '' OR m.brand ILIKE %(marca)s)
            ORDER BY o.unit_price ASC;
            """,
            {
                "potencia_minima_wp": potencia_minima_wp,
                "marca": f"%{marca}%" if marca else "",
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
