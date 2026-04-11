from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings


def get_engine() -> AsyncEngine:
    settings = get_settings()
    if not settings.async_database_url:
        raise RuntimeError("DATABASE_URL is required for database-backed intelligence APIs.")
    return create_async_engine(settings.async_database_url, pool_pre_ping=True, pool_recycle=1800, future=True)


def get_session_factory(settings: Settings | None = None) -> async_sessionmaker:
    engine = get_engine() if settings is None else create_async_engine(settings.async_database_url, pool_pre_ping=True, future=True)
    return async_sessionmaker(engine, expire_on_commit=False)
