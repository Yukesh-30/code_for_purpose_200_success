from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the FlowSight AI Flask intelligence service."""

    app_name: str = "FlowSight Talk-to-Data Intelligence"
    environment: Literal["local", "development", "staging", "production"] = "local"
    database_url: str = ""
    timezone: str = "Asia/Calcutta"
    max_result_rows: int = 500
    query_timeout_seconds: int = 20
    vector_store_path: str = "./.chroma"
    vector_collection_name: str = "financial_semantics"
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    enable_llm: bool = False
    min_analysis_rows: int = 1
    min_forecast_history_days: int = 7
    ideal_forecast_history_days: int = 21
    min_anomaly_transactions: int = 10
    anomaly_contamination: float = 0.05
    anomaly_iqr_multiplier: float = 2.5
    low_confidence_threshold: float = 0.65
    low_balance_threshold: float = 100000.0
    vendor_concentration_threshold: float = 25.0
    category_concentration_threshold: float = 30.0
    expense_approval_threshold: float = 10000.0
    reserve_days_target: int = 60

    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("postgresql+asyncpg://"):
            return _normalize_asyncpg_url(self.database_url)
        if self.database_url.startswith("postgresql://"):
            return _normalize_asyncpg_url(
                self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            )
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "FlowSight Talk-to-Data Intelligence"),
        environment=os.getenv("ENVIRONMENT", "local"),
        database_url=os.getenv("DATABASE_URL", ""),
        timezone=os.getenv("APP_TIMEZONE", "Asia/Calcutta"),
        max_result_rows=int(os.getenv("MAX_RESULT_ROWS", "500")),
        query_timeout_seconds=int(os.getenv("QUERY_TIMEOUT_SECONDS", "20")),
        vector_store_path=os.getenv("VECTOR_STORE_PATH", "./.chroma"),
        vector_collection_name=os.getenv("VECTOR_COLLECTION_NAME", "financial_semantics"),
        llm_base_url=os.getenv("LLM_BASE_URL", ""),
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_provider=os.getenv("LLM_PROVIDER", "groq"),
        llm_model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        enable_llm=os.getenv("ENABLE_LLM", "false").lower() in {"1", "true", "yes", "on"},
        min_analysis_rows=int(os.getenv("MIN_ANALYSIS_ROWS", "1")),
        min_forecast_history_days=int(os.getenv("MIN_FORECAST_HISTORY_DAYS", "7")),
        ideal_forecast_history_days=int(os.getenv("IDEAL_FORECAST_HISTORY_DAYS", "21")),
        min_anomaly_transactions=int(os.getenv("MIN_ANOMALY_TRANSACTIONS", "10")),
        anomaly_contamination=float(os.getenv("ANOMALY_CONTAMINATION", "0.05")),
        anomaly_iqr_multiplier=float(os.getenv("ANOMALY_IQR_MULTIPLIER", "2.5")),
        low_confidence_threshold=float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.65")),
        low_balance_threshold=float(os.getenv("LOW_BALANCE_THRESHOLD", "100000")),
        vendor_concentration_threshold=float(os.getenv("VENDOR_CONCENTRATION_THRESHOLD", "25")),
        category_concentration_threshold=float(os.getenv("CATEGORY_CONCENTRATION_THRESHOLD", "30")),
        expense_approval_threshold=float(os.getenv("EXPENSE_APPROVAL_THRESHOLD", "10000")),
        reserve_days_target=int(os.getenv("RESERVE_DAYS_TARGET", "60")),
    )


def _normalize_asyncpg_url(url: str) -> str:
    normalized = url.replace("sslmode=require", "ssl=require")
    return normalized.replace("&channel_binding=require", "").replace(
        "?channel_binding=require&", "?"
    )
