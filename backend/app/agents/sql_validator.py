from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.semantic.definitions import CANONICAL_SCHEMA, CURRENT_NEON_SCHEMA


FORBIDDEN_RE = re.compile(r"\b(insert|update|delete|drop|truncate|alter|create|grant|revoke|merge|call|copy|execute|vacuum|analyze)\b", re.IGNORECASE)


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    sql: str
    error: str | None = None


class SQLValidator:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.allowed_schema = {**CANONICAL_SCHEMA, **CURRENT_NEON_SCHEMA}

    def validate(
        self,
        sql: str,
        business_id: int,
        schema_context: dict[str, list[str]] | None = None,
    ) -> ValidationResult:
        stripped = sql.strip().rstrip(";")
        if not stripped:
            return ValidationResult(False, stripped, "No SQL was generated.")
        if ";" in stripped:
            return ValidationResult(False, stripped, "Multiple SQL statements are not allowed.")
        if FORBIDDEN_RE.search(stripped):
            return ValidationResult(False, stripped, "Only read-only SELECT queries are allowed.")
        if not re.match(r"^(select|with)\b", stripped, flags=re.IGNORECASE):
            return ValidationResult(False, stripped, "SQL must start with SELECT or WITH.")
        if not re.search(rf"\bbusiness_id\s*=\s*{int(business_id)}\b", stripped, flags=re.IGNORECASE):
            return ValidationResult(False, stripped, "Query must be scoped to the requested business_id.")
        if re.search(r"\bmax\s*\(\s*balance_after_transaction\s*\)", stripped, flags=re.IGNORECASE):
            return ValidationResult(False, stripped, "Closing balance must use the latest ordered transaction, not MAX(balance_after_transaction).")

        schema_error = self._validate_schema(stripped, schema_context=schema_context)
        if schema_error:
            return ValidationResult(False, stripped, schema_error)
        return ValidationResult(True, self._enforce_limit(stripped))

    def _validate_schema(self, sql: str, schema_context: dict[str, list[str]] | None = None) -> str | None:
        allowed_schema = {
            table: set(columns)
            for table, columns in (schema_context or self.allowed_schema).items()
        }
        if schema_context is not None and not allowed_schema:
            return "Selected schema context is empty."
        try:
            import sqlglot
            from sqlglot import exp
        except ImportError:
            return self._fallback_table_validation(sql, allowed_schema)

        try:
            tree = sqlglot.parse_one(sql, read="postgres")
        except Exception as exc:
            return f"SQL parser rejected the query: {exc}"

        tables = {table.name for table in tree.find_all(exp.Table)}
        unknown_tables = tables - set(allowed_schema)
        if unknown_tables:
            return f"Unknown or disallowed tables: {', '.join(sorted(unknown_tables))}."
            
        # Basic AST check: MUST have a Where clause if querying tables
        if tables and not any(tree.find_all(exp.Where)):
            return "Query must have a WHERE clause scoping the business_id."

        for column in tree.find_all(exp.Column):
            table_name = column.table
            column_name = column.name
            if table_name and table_name in allowed_schema and column_name not in allowed_schema[table_name]:
                return f"Unknown column {table_name}.{column_name}."
            if not table_name and len(tables) == 1:
                table = next(iter(tables))
                if column_name not in allowed_schema.get(table, set()) and column_name != "*":
                    # Allow SQL aliases and generated aggregate names by checking raw source tokens only.
                    if not re.search(rf"\bas\s+{re.escape(column_name)}\b", sql, flags=re.IGNORECASE):
                        return f"Unknown column {table}.{column_name}."
        return None

    def _fallback_table_validation(self, sql: str, allowed_schema: dict[str, set[str]]) -> str | None:
        pairs = re.findall(r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)|\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE)
        flat_tables = {name for pair in pairs for name in pair if name}
        unknown = flat_tables - set(allowed_schema)
        if unknown:
            return f"Unknown or disallowed tables: {', '.join(sorted(unknown))}."
        return None

    def _enforce_limit(self, sql: str) -> str:
        if re.search(r"\blimit\s+\d+\b", sql, flags=re.IGNORECASE):
            return re.sub(
                r"\blimit\s+(\d+)\b",
                lambda match: f"LIMIT {min(int(match.group(1)), self.settings.max_result_rows)}",
                sql,
                flags=re.IGNORECASE,
            )
        return f"{sql}\nLIMIT {self.settings.max_result_rows}"
