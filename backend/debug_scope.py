from app.agents.semantic_parser import parse_query

tests = [
    ("what is 2+3",                    "out_of_scope"),
    ("what is the weather",            "out_of_scope"),
    ("tell me a joke",                 "out_of_scope"),
    ("who is the president",           "out_of_scope"),
    ("what was my cashflow last month","analytics"),
    ("show invoices",                  "analytics"),
    ("forecast next 30 days",          "forecast"),
    ("find unusual transactions",      "anomaly"),
    ("hi hello",                       "out_of_scope"),
    ("what is my balance",             "analytics"),
    ("what is 2+3 in my expenses",     "analytics"),  # has financial context
]

print("=== Scope Detection via Semantic Scoring ===\n")
passed = 0
for q, expected in tests:
    r = parse_query(q)
    total = sum(r.concept_scores.values())
    has_time = r.time_label not in ("unspecified",)
    # Replicate IntentAgent._MIN_FINANCIAL_SCORE logic
    is_off_topic = total < 0.05 and not has_time
    actual = "out_of_scope" if is_off_topic else r.intent_type
    ok = actual == expected
    if ok: passed += 1
    sym = "✅" if ok else "❌"
    print(f"{sym} '{q}'")
    print(f"   score={total:.4f}  intent_from_parser={r.intent_type}  final={actual}  expected={expected}")
    print()

print(f"Score: {passed}/{len(tests)}")
