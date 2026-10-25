"""Conexão com o Postgres 'Negócio', via pool."""

from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from settings import settings

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        _pool = pool.ThreadedConnectionPool(
            minconn=1, maxconn=10, dsn=settings.DATABASE_URL
        )
    return _pool


@contextmanager
def get_cursor():
    conn = _get_pool().getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _get_pool().putconn(conn)


def ping(timeout: int) -> None:
    """Abre uma conexão própria, fora do pool, e roda SELECT 1."""
    conn = psycopg2.connect(settings.DATABASE_URL, connect_timeout=timeout)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
    finally:
        conn.close()
