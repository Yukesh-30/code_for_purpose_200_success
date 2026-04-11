from app.agents.semantic_parser import parse_query, CONCEPT_VOCABULARY, _semantic_score

q = "Why did my cashflow decline last 2 months vs previous 2 months and what should I do?"
print(f"Q: {q}\n")

scores = {c: _semantic_score(q, v) for c, v in CONCEPT_VOCABULARY.items()}
for concept, score in sorted(scores.items(), key=lambda x: -x[1]):
    if score > 0:
        matched = [p for p in CONCEPT_VOCABULARY[concept] if p.lower() in q.lower()]
        print(f"  {concept}: {score:.4f}  matched={matched}")

result = parse_query(q)
print(f"\nintent={result.intent_type}  confidence={result.confidence}")
print(f"concepts={result.concepts}")
print(f"is_complex={result.is_complex}")
