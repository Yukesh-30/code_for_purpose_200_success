from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _get_conn_str() -> str:
    url = os.getenv("DATABASE_URL", "")
    return url.replace("&channel_binding=require", "").replace("?channel_binding=require&", "?")


class QueryExecutor:
    """Synchronous psycopg2 executor — read-only, with statement timeout."""

    def __init__(self, max_rows: int = 500, **_kwargs) -> None:
        self.max_rows = max_rows
        self._conn_str = _get_conn_str()

    async def fetch_all(self, sql: str, *, validated: bool = False) -> tuple[list[str], list[dict[str, Any]], bool]:
        """Async signature kept for LangGraph compatibility — delegates to sync."""
        return self._fetch_sync(sql, validated=validated)

    def _fetch_sync(self, sql: str, *, validated: bool = False) -> tuple[list[str], list[dict[str, Any]], bool]:
        import psycopg2
        import psycopg2.extras

        if not validated:
            raise RuntimeError("Refusing to execute SQL that was not marked as validated.")

        conn = psycopg2.connect(self._conn_str)
        try:
            conn.set_session(readonly=True, autocommit=True)
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Enforce query timeout
                timeout_ms = int(os.getenv("QUERY_TIMEOUT_SECONDS", "20")) * 1000
                cur.execute(f"SET statement_timeout = {timeout_ms}")
                cur.execute(sql)
                rows = cur.fetchall()
                columns = [d.name for d in cur.description] if cur.description else []
        finally:
            conn.close()

        truncated = len(rows) > self.max_rows
        kept = rows[: self.max_rows]
        return columns, [{k: _json_safe(v) for k, v in row.items()} for row in kept], truncated
