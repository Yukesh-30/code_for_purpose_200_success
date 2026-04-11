from __future__ import annotations

import pandas as pd
import numpy as np

from app.agents.state import AgentState
from app.core.config import Settings, get_settings
from app.schemas.api import ChartData

class AnomalyAgent:
    """
    Context-aware Anomaly detection:
    Uses sklearn IsolationForest with features:
    - amount
    - day_of_week
    - transaction_type_encoded
    Falls back to simple IQR bounds if ML fails or insufficient rows are passed.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def detect(self, state: AgentState) -> AgentState:
        rows = state.get("rows", [])
        if len(rows) < self.settings.min_anomaly_transactions:
            state["status"] = "insufficient_data"
            state["analysis"] = {"reason": f"At least {self.settings.min_anomaly_transactions} transactions are required for anomaly detection."}
            state["chart"] = ChartData(type="none")
            return state

        anomalies = []
        method_used = ""

        try:
            from sklearn.ensemble import IsolationForest
            
            # Prepare feature set
            df = pd.DataFrame(rows)
            df['amount'] = df['amount'].astype(float)
            
            # Context feature 1: day of week
            if "transaction_date" in df.columns:
                df['day_of_week'] = pd.to_datetime(df['transaction_date']).dt.dayofweek
            else:
                df['day_of_week'] = 0
                
            # Context feature 2: transaction type
            if "transaction_type" in df.columns:
                df['type_encoded'] = df['transaction_type'].apply(lambda x: 1 if str(x).lower() == 'credit' else 0)
            else:
                df['type_encoded'] = 0
                
            features = df[['amount', 'day_of_week', 'type_encoded']].values
            
            model = IsolationForest(contamination=self.settings.anomaly_contamination, random_state=42)
            preds = model.fit_predict(features)
            
            for i, row in enumerate(rows):
                if preds[i] == -1:
                    enriched = dict(row)
                    enriched["detection_methods"] = "Isolation Forest (Contextual)"
                    enriched["reason"] = f"Unusual amount/timing context for {row.get('transaction_type', 'transaction')}"
                    anomalies.append(enriched)
                    
            method_used = "isolation_forest_ml"
            
        except Exception as e:
            # Safe Fallback: IQR
            amounts = [float(r.get("amount") or 0) for r in rows]
            sorted_amounts = sorted(amounts)
            n = len(sorted_amounts)
            q1 = sorted_amounts[n // 4]
            q3 = sorted_amounts[(3 * n) // 4]
            iqr = q3 - q1
            iqr_lower = q1 - self.settings.anomaly_iqr_multiplier * iqr
            iqr_upper = q3 + self.settings.anomaly_iqr_multiplier * iqr
            
            for row in rows:
                amt = float(row.get("amount", 0))
                if amt < iqr_lower or amt > iqr_upper:
                    enriched = dict(row)
                    enriched["detection_methods"] = "IQR Bounds"
                    enriched["reason"] = f"Amount {amt} is statistically outside normal range."
                    anomalies.append(enriched)

            method_used = "iqr_fallback"

        state["anomalies"] = anomalies
        # Keep rows untouched since we introduced a separate `anomalies` field in AgentState,
        # but to keep backward compatibility with chart renderer which uses rows:
        state["rows"] = anomalies

        state["columns"] = (
            list(anomalies[0].keys()) if anomalies
            else list(rows[0].keys()) + ["detection_methods", "reason"]
        )
        state["analysis"] = {
            "method": method_used,
            "lookback_transactions": len(rows),
            "anomaly_count": len(anomalies)
        }
        state["chart"] = ChartData(type="table", series=anomalies[:50])
        state["status"] = "success"
        return state
