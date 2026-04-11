from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from statistics import mean, stdev

from app.agents.state import AgentState
from app.core.config import Settings, get_settings
from app.schemas.api import ChartData


class ForecastAgent:
    """
    Cashflow forecasting agent.
    Method cascade:
      1. XGBoost (feature-engineered ML)
      2. Prophet (if installed)
      3. ARIMA   (if statsmodels installed)
      4. Rolling Mean + Trend + Seasonality (always works)
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    # ── XGBoost forecast ──────────────────────────────────────────────────────
    def _xgboost_forecast(self, history_rows: list, horizon_days: int,
                          last_date: date, last_balance: float) -> dict | None:
        try:
            import numpy as np
            import pandas as pd
            from xgboost import XGBRegressor

            df = pd.DataFrame(history_rows)
            df["ds"] = pd.to_datetime(df["cashflow_date"])
            df["y"]  = df["net_cashflow"].astype(float)
            df = df.sort_values("ds").reset_index(drop=True)

            # Feature engineering
            df["day_of_week"]  = df["ds"].dt.dayofweek
            df["day_of_month"] = df["ds"].dt.day
            df["month"]        = df["ds"].dt.month
            df["week_of_year"] = df["ds"].dt.isocalendar().week.astype(int)
            df["lag_1"]        = df["y"].shift(1).fillna(0)
            df["lag_7"]        = df["y"].shift(7).fillna(0)
            df["lag_14"]       = df["y"].shift(14).fillna(0)
            df["rolling_7"]    = df["y"].rolling(7,  min_periods=1).mean()
            df["rolling_14"]   = df["y"].rolling(14, min_periods=1).mean()
            df["rolling_std7"] = df["y"].rolling(7,  min_periods=1).std().fillna(0)

            features = ["day_of_week", "day_of_month", "month", "week_of_year",
                        "lag_1", "lag_7", "lag_14", "rolling_7", "rolling_14", "rolling_std7"]
            X = df[features].values
            y = df["y"].values

            model = XGBRegressor(
                n_estimators=200, max_depth=4, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8,
                random_state=42, verbosity=0,
            )
            model.fit(X, y)

            # Build future feature rows
            avg_inflow  = float(df.get("inflow",  pd.Series([0])).mean() if "inflow"  in df else 0)
            avg_outflow = float(df.get("outflow", pd.Series([0])).mean() if "outflow" in df else 0)
            avg_net     = float(df["y"].mean())

            recent_vals = list(df["y"].values[-14:])
            forecast_rows = []
            balance = last_balance

            for offset in range(1, horizon_days + 1):
                fdate = last_date + timedelta(days=offset)
                n     = len(recent_vals)
                feat  = np.array([[
                    fdate.weekday(),
                    fdate.day,
                    fdate.month,
                    int(fdate.strftime("%W")),
                    recent_vals[-1]  if n >= 1  else 0,
                    recent_vals[-7]  if n >= 7  else 0,
                    recent_vals[-14] if n >= 14 else 0,
                    float(np.mean(recent_vals[-7:])),
                    float(np.mean(recent_vals[-14:])),
                    float(np.std(recent_vals[-7:]) if len(recent_vals) >= 2 else 0),
                ]])
                pred_net = float(model.predict(feat)[0])
                recent_vals.append(pred_net)
                balance += pred_net

                delta = pred_net - avg_net
                forecast_rows.append({
                    "forecast_date":             fdate.isoformat(),
                    "predicted_inflow":          round(max(0, avg_inflow  + max(0, delta)), 2),
                    "predicted_outflow":         round(max(0, avg_outflow + abs(min(0, delta))), 2),
                    "predicted_net_cashflow":    round(pred_net, 2),
                    "predicted_closing_balance": round(balance,  2),
                })

            return {
                "rows":        forecast_rows,
                "method":      "xgboost_ml",
                "avg_inflow":  round(avg_inflow,  2),
                "avg_outflow": round(avg_outflow, 2),
                "avg_net":     round(avg_net,     2),
            }

        except Exception:
            return None

    # ── Rolling mean + trend + seasonality (always works) ─────────────────────
    def _rolling_forecast(self, history_rows: list, horizon_days: int,
                          last_date: date, last_balance: float) -> dict:
        inflows  = [float(r.get("inflow")  or 0) for r in history_rows]
        outflows = [float(r.get("outflow") or 0) for r in history_rows]
        nets     = [i - o for i, o in zip(inflows, outflows)]
        n        = len(nets)

        avg_inflow  = mean(inflows)
        avg_outflow = mean(outflows)
        avg_net     = avg_inflow - avg_outflow

        # Linear trend
        slope = 0.0
        if n >= self.settings.ideal_forecast_history_days:
            xs     = list(range(n))
            xm, ym = mean(xs), mean(nets)
            denom  = sum((x - xm) ** 2 for x in xs) or 1
            slope  = sum((x - xm) * (y - ym) for x, y in zip(xs, nets)) / denom

        # Day-of-week seasonality
        from datetime import date as _date
        dow: dict[int, list[float]] = {i: [] for i in range(7)}
        for i, row in enumerate(history_rows):
            try:
                d = _date.fromisoformat(str(row.get("cashflow_date", ""))[:10])
                dow[d.weekday()].append(nets[i])
            except ValueError:
                pass
        dow_avg = {k: mean(v) if v else avg_net for k, v in dow.items()}

        forecast_rows = []
        balance = last_balance
        for offset in range(1, horizon_days + 1):
            fdate  = last_date + timedelta(days=offset)
            trend  = slope * (n + offset)
            ratio  = (dow_avg[fdate.weekday()] / avg_net) if avg_net != 0 else 1.0
            ratio  = max(0.5, min(2.0, ratio))
            pred_net    = (avg_net + trend) * ratio
            pred_inflow = max(0.0, avg_inflow  * ratio)
            pred_outflow= max(0.0, avg_outflow * ratio)
            balance    += pred_net
            forecast_rows.append({
                "forecast_date":             fdate.isoformat(),
                "predicted_inflow":          round(pred_inflow,  2),
                "predicted_outflow":         round(pred_outflow, 2),
                "predicted_net_cashflow":    round(pred_net,     2),
                "predicted_closing_balance": round(balance,      2),
            })

        return {
            "rows":        forecast_rows,
            "method":      "rolling_mean_trend_seasonality",
            "avg_inflow":  round(avg_inflow,  2),
            "avg_outflow": round(avg_outflow, 2),
            "avg_net":     round(avg_net,     2),
        }

    # ── Main entry point ──────────────────────────────────────────────────────
    def forecast(self, state: AgentState) -> AgentState:
        if not state.get("horizon_days"):
            state["status"] = "needs_clarification"
            state["analysis"] = {"reason": "Forecast horizon is required."}
            state["chart"] = ChartData(type="none")
            return state
        horizon_days = int(state["horizon_days"])
        history_rows = state.get("rows", [])

        if len(history_rows) < self.settings.min_forecast_history_days:
            state["status"]   = "insufficient_data"
            state["analysis"] = {
                "reason": (
                    f"Need at least {self.settings.min_forecast_history_days} days of cashflow history. "
                    f"Only {len(history_rows)} days found."
                )
            }
            state["chart"] = ChartData(type="none")
            state.setdefault("warnings", []).append(
                f"Insufficient history: {len(history_rows)} days found, {self.settings.min_forecast_history_days} required."
            )
            return state

        # Parse last date and balance
        last_row = history_rows[-1]
        try:
            last_date = date.fromisoformat(str(last_row.get("cashflow_date", ""))[:10])
        except ValueError:
            state["status"] = "insufficient_data"
            state["analysis"] = {"reason": "Forecast history contains an invalid last cashflow_date."}
            state["chart"] = ChartData(type="none")
            return state
        if last_row.get("closing_balance") is None:
            state["status"] = "insufficient_data"
            state["analysis"] = {"reason": "Forecast history is missing closing_balance for the latest row."}
            state["chart"] = ChartData(type="none")
            return state
        last_balance = float(last_row.get("closing_balance"))

        as_of = state.get("as_of_date") or datetime.now(ZoneInfo(self.settings.timezone)).date()
        if last_date > as_of:
            state["status"] = "insufficient_data"
            state["analysis"] = {"reason": "Forecast history contains dates after the request as_of_date."}
            state["chart"] = ChartData(type="none")
            return state

        # Validate data has real values
        total_inflow  = sum(float(r.get("inflow")  or 0) for r in history_rows)
        total_outflow = sum(float(r.get("outflow") or 0) for r in history_rows)
        if total_inflow == 0 and total_outflow == 0:
            state["status"]   = "insufficient_data"
            state["analysis"] = {"reason": "History rows contain no inflow or outflow data."}
            state["chart"]    = ChartData(type="none")
            return state

        # ── Try XGBoost → Prophet → ARIMA → Rolling ───────────────────────────
        result = self._xgboost_forecast(history_rows, horizon_days, last_date, last_balance)

        if not result:
            try:
                import pandas as pd
                from prophet import Prophet
                df       = pd.DataFrame(history_rows)
                df["ds"] = pd.to_datetime(df["cashflow_date"])
                df["y"]  = df["net_cashflow"].astype(float)
                model    = Prophet(weekly_seasonality=True, daily_seasonality=False,
                                   changepoint_prior_scale=0.05)
                model.fit(df)
                future   = model.make_future_dataframe(periods=horizon_days)
                fc       = model.predict(future).tail(horizon_days)
                inflows  = [float(r.get("inflow")  or 0) for r in history_rows]
                outflows = [float(r.get("outflow") or 0) for r in history_rows]
                avg_in, avg_out = mean(inflows), mean(outflows)
                avg_net  = mean([float(r.get("net_cashflow") or 0) for r in history_rows])
                balance  = last_balance
                rows_out = []
                for _, row in fc.iterrows():
                    pred_net = float(row["yhat"])
                    balance += pred_net
                    delta    = pred_net - avg_net
                    rows_out.append({
                        "forecast_date":             pd.to_datetime(row["ds"]).date().isoformat(),
                        "predicted_inflow":          round(max(0, avg_in  + max(0, delta)), 2),
                        "predicted_outflow":         round(max(0, avg_out + abs(min(0, delta))), 2),
                        "predicted_net_cashflow":    round(pred_net, 2),
                        "predicted_closing_balance": round(balance,  2),
                    })
                result = {"rows": rows_out, "method": "prophet_ml",
                          "avg_inflow": round(avg_in, 2), "avg_outflow": round(avg_out, 2),
                          "avg_net": round(avg_net, 2)}
            except Exception:
                pass

        if not result:
            try:
                from statsmodels.tsa.arima.model import ARIMA
                data     = [float(r.get("net_cashflow") or 0) for r in history_rows]
                fit      = ARIMA(data, order=(5, 1, 0)).fit()
                preds    = fit.forecast(steps=horizon_days)
                inflows  = [float(r.get("inflow")  or 0) for r in history_rows]
                outflows = [float(r.get("outflow") or 0) for r in history_rows]
                avg_in, avg_out, avg_net = mean(inflows), mean(outflows), mean(data)
                balance  = last_balance
                rows_out = []
                for offset, pred_net in enumerate(preds, start=1):
                    fdate = last_date + timedelta(days=offset)
                    balance += pred_net
                    delta   = pred_net - avg_net
                    rows_out.append({
                        "forecast_date":             fdate.isoformat(),
                        "predicted_inflow":          round(max(0, avg_in  + max(0, delta)), 2),
                        "predicted_outflow":         round(max(0, avg_out + abs(min(0, delta))), 2),
                        "predicted_net_cashflow":    round(pred_net, 2),
                        "predicted_closing_balance": round(balance,  2),
                    })
                result = {"rows": rows_out, "method": "arima_statsmodels",
                          "avg_inflow": round(avg_in, 2), "avg_outflow": round(avg_out, 2),
                          "avg_net": round(avg_net, 2)}
            except Exception:
                pass

        if not result:
            result = self._rolling_forecast(history_rows, horizon_days, last_date, last_balance)

        forecast_rows = result["rows"]
        if not forecast_rows:
            state["status"]   = "insufficient_data"
            state["analysis"] = {"reason": "Forecast model produced no output rows."}
            state["chart"]    = ChartData(type="none")
            return state

        avg_inflow  = result.get("avg_inflow",  mean(r["predicted_inflow"]  for r in forecast_rows))
        avg_outflow = result.get("avg_outflow", mean(r["predicted_outflow"] for r in forecast_rows))
        avg_net     = result.get("avg_net",     mean(r["predicted_net_cashflow"] for r in forecast_rows))
        neg_days    = sum(1 for r in forecast_rows if r["predicted_net_cashflow"] < 0)
        end_balance = forecast_rows[-1]["predicted_closing_balance"]

        state["forecast"] = {
            "rows":                     forecast_rows,
            "method":                   result["method"],
            "horizon_days":             horizon_days,
            "history_days":             len(history_rows),
            "projected_ending_balance": end_balance,
            "negative_cashflow_days":   neg_days,
            "avg_inflow":               round(avg_inflow,  2),
            "avg_outflow":              round(avg_outflow, 2),
            "avg_net":                  round(avg_net,     2),
        }
        state["rows"]    = forecast_rows
        state["columns"] = list(forecast_rows[0].keys())
        state["chart"]   = ChartData(
            type="area",
            x="forecast_date",
            y=["predicted_inflow", "predicted_outflow", "predicted_closing_balance"],
            series=forecast_rows,
        )
        state["status"] = "success"

        if len(history_rows) < self.settings.ideal_forecast_history_days:
            state.setdefault("warnings", []).append(
                f"Only {len(history_rows)} days of history. "
                f"{self.settings.ideal_forecast_history_days}+ days recommended for higher accuracy."
            )
        return state
