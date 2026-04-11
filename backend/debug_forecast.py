import importlib, sys

# Force fresh import
for mod in list(sys.modules.keys()):
    if 'app' in mod:
        del sys.modules[mod]

from app.agents.semantic_parser import parse_query, CONCEPT_VOCABULARY, _semantic_score

q = "forecast next 30 days"
r = parse_query(q)
print(f"Q: {q}")
print(f"intent_type={r.intent_type}")
print(f"forecast_score={r.concept_scores.get('forecast', 0):.4f}")
print(f"net_score={r.concept_scores.get('net_position', 0):.4f}")
print(f"anomaly_score={r.concept_scores.get('anomalies', 0):.4f}")
print(f"is_complex={r.is_complex}")
print(f"wants_forecast={r.wants_forecast}")

# Manual check
fs = r.concept_scores.get('forecast', 0)
ns = r.concept_scores.get('net_position', 0)
as_ = r.concept_scores.get('anomalies', 0)
strong = fs >= 0.1 and fs > as_ * 1.5 and fs >= ns * 0.5
print(f"\nManual strong_forecast={strong}")
print(f"  fs={fs} >= 0.1: {fs >= 0.1}")
print(f"  fs > as*1.5: {fs} > {as_*1.5}: {fs > as_*1.5}")
print(f"  fs >= ns*0.5: {fs} >= {ns*0.5}: {fs >= ns*0.5}")
