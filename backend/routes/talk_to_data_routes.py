from __future__ import annotations

from datetime import date

from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

from app.agents.state import AgentState
from app.runtime import get_graph
from app.schemas.api import AnomalyRequest, ChatRequest, ForecastRequest, IntelligenceResponse
from app.services.time_context import TimeContextResolver
from middleware.auth import require_auth
from routes.upload_routes import get_business_id

talk_bp = Blueprint("talk_to_data", __name__)


def _json_response(response: IntelligenceResponse, include_sql: bool = True):
    payload = response.model_dump(mode="json") if hasattr(response, "model_dump") else response.dict()
    if not include_sql:
        payload["sql"] = None
    return jsonify(payload), 200


def _validation_error(error: ValidationError):
    return jsonify({
        "status": "error",
        "message": "Invalid request payload",
        "details": error.errors(),
    }), 400


def _check_access(biz_id: int) -> bool:
    """Return True if the current user may query this business."""
    if g.role in ('admin', 'relationship_manager'):
        return True
    user_biz = get_business_id(g.user_id)
    return user_biz is None or biz_id == user_biz


def _parse_payload(model, payload: dict):
    return model.model_validate(payload) if hasattr(model, "model_validate") else model.parse_obj(payload)


def _today() -> date:
    return TimeContextResolver().today()


def _reject_future_as_of(as_of: date | None):
    if as_of and as_of > _today():
        return jsonify({"status": "error", "message": "as_of_date cannot be in the future."}), 400
    return None


@talk_bp.route("/chat", methods=["POST"])
@require_auth
def chat():
    try:
        payload = _parse_payload(ChatRequest, request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return _validation_error(e)
    future_error = _reject_future_as_of(payload.as_of_date)
    if future_error:
        return future_error

    biz_id = int(payload.business_id)
    if not _check_access(biz_id):
        return jsonify({'error': 'Access denied to this business data'}), 403

    state: AgentState = {
        "business_id": biz_id,
        "user_id": g.user_id,
        "question": payload.question,
        "history": payload.history,
        "as_of_date": payload.as_of_date,
    }
    response = get_graph().run_sync(state)
    return _json_response(response, include_sql=payload.include_sql)


@talk_bp.route("/forecast", methods=["POST"])
@require_auth
def forecast():
    try:
        payload = _parse_payload(ForecastRequest, request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return _validation_error(e)
    future_error = _reject_future_as_of(payload.as_of_date)
    if future_error:
        return future_error

    biz_id = int(payload.business_id)
    if not _check_access(biz_id):
        return jsonify({'error': 'Access denied to this business data'}), 403

    state: AgentState = {
        "business_id": biz_id,
        "user_id": g.user_id,
        "question": f"Forecast cashflow for the next {payload.horizon_days} days",
        "history": [],
        "as_of_date": payload.as_of_date or _today(),
        "horizon_days": payload.horizon_days,
    }
    response = get_graph().run_sync(state, horizon_days=payload.horizon_days)
    return _json_response(response, include_sql=payload.include_sql)


@talk_bp.route("/anomaly", methods=["POST"])
@require_auth
def anomaly():
    try:
        payload = _parse_payload(AnomalyRequest, request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return _validation_error(e)
    future_error = _reject_future_as_of(payload.as_of_date)
    if future_error:
        return future_error

    biz_id = int(payload.business_id)
    if not _check_access(biz_id):
        return jsonify({'error': 'Access denied to this business data'}), 403

    state: AgentState = {
        "business_id": biz_id,
        "user_id": g.user_id,
        "question": f"Find unusual transactions in the last {payload.lookback_days} days",
        "history": [],
        "as_of_date": payload.as_of_date or _today(),
    }
    response = get_graph().run_sync(state)
    return _json_response(response, include_sql=payload.include_sql)
