"""Final smoke test — verifies all critical paths work."""
import urllib.request, urllib.error, json, sys

BASE = "http://127.0.0.1:5000"
PASS, FAIL = 0, 0

def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}  {detail}")

def post(path, payload, token=None):
    hdrs = {"Content-Type": "application/json"}
    if token: hdrs["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE+path,
        data=json.dumps(payload).encode(), headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {}

def get(path, token=None):
    hdrs = {}
    if token: hdrs["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE+path, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {}

print("\n" + "="*55)
print("  FLOWSIGHT AI — FINAL SMOKE TEST")
print("="*55)

# ── Health ────────────────────────────────────────────────────
print("\n[1] Server health")
s, d = get("/health")
check("GET /health → 200", s == 200, f"got {s}")
check("Service name present", "FlowSight" in str(d))

# ── Auth ──────────────────────────────────────────────────────
print("\n[2] Authentication")
s, d = post("/auth/login", {"email": "arun@freshmart.com", "password": "password123"})
check("POST /auth/login → 200", s == 200, f"got {s}")
check("JWT token returned", bool(d.get("access_token")))
check("business_id returned", d.get("business_id") is not None)
TOKEN = d.get("access_token", "")
BID   = d.get("business_id", 1)

# ── Chat — cashflow ───────────────────────────────────────────
print("\n[3] Chat — cashflow query")
s, d = post("/chat", {"business_id": BID, "question": "What was my cashflow last month?", "include_sql": True}, TOKEN)
check("POST /chat → 200", s == 200, f"got {s}")
check("status=success", d.get("status") == "success", d.get("status"))
check("answer not empty", bool(d.get("answer")))
check("SQL returned", bool(d.get("sql")))
check("rows returned", d.get("supporting_data", {}).get("row_count", 0) > 0)

# ── Chat — invoice ────────────────────────────────────────────
print("\n[4] Chat — invoice query (was crashing)")
s, d = post("/chat", {"business_id": BID, "question": "invoice", "include_sql": False}, TOKEN)
check("POST /chat invoice → 200 (not 500)", s == 200, f"got {s}")
check("status=success or clarification", d.get("status") in ("success","needs_clarification"))

# ── Chat — out of scope ───────────────────────────────────────
print("\n[5] Chat — out of scope")
s, d = post("/chat", {"business_id": BID, "question": "what is the weather today", "include_sql": False}, TOKEN)
check("POST /chat out-of-scope → 200", s == 200, f"got {s}")
check("status=out_of_scope", d.get("status") == "out_of_scope", d.get("status"))

# ── Chat — ambiguous ──────────────────────────────────────────
print("\n[6] Chat — ambiguous query")
s, d = post("/chat", {"business_id": BID, "question": "show performance", "include_sql": False}, TOKEN)
check("POST /chat ambiguous → 200", s == 200, f"got {s}")
check("asks for clarification", d.get("status") in ("needs_clarification","out_of_scope"), d.get("status"))

# ── Forecast ──────────────────────────────────────────────────
print("\n[7] Forecast endpoint")
s, d = post("/forecast", {"business_id": BID, "horizon_days": 30}, TOKEN)
check("POST /forecast → 200", s == 200, f"got {s}")
check("status=success", d.get("status") == "success", d.get("status"))
check("30 forecast rows", d.get("supporting_data", {}).get("row_count", 0) == 30)
check("answer mentions balance", "balance" in d.get("answer","").lower() or "₹" in d.get("answer",""))

# ── Anomaly ───────────────────────────────────────────────────
print("\n[8] Anomaly endpoint")
s, d = post("/anomaly", {"business_id": BID, "lookback_days": 90}, TOKEN)
check("POST /anomaly → 200", s == 200, f"got {s}")
check("status=success", d.get("status") == "success", d.get("status"))
check("anomalies found", d.get("supporting_data", {}).get("row_count", 0) > 0)

# ── Dashboard stats ───────────────────────────────────────────
print("\n[9] Dashboard stats")
s, d = get(f"/stats?business_id={BID}", TOKEN)
check("GET /stats → 200", s == 200, f"got {s}")
check("balance present", "balance" in d)
check("cashflow present", "cashflow" in d)
check("risk_score present", "risk_score" in d)

# ── Complex multi-step ────────────────────────────────────────
print("\n[10] Complex multi-step query")
s, d = post("/chat", {
    "business_id": BID,
    "question": "Why did my cashflow decline last 2 months vs previous 2 months and what should I do?",
    "include_sql": False
}, TOKEN)
check("POST /chat complex → 200", s == 200, f"got {s}")
check("intent=complex", d.get("intent") == "complex", d.get("intent"))
check("driver_analysis present", bool(d.get("driver_analysis")))
check("recommendations present", bool(d.get("recommendations")))

# ── Summary ───────────────────────────────────────────────────
print(f"\n{'='*55}")
total = PASS + FAIL
print(f"  {PASS}/{total} checks passed  {'🏆 ALL GOOD' if FAIL == 0 else f'⚠️  {FAIL} failed'}")
print("="*55)
print(f"\n  Backend  → http://localhost:5000")
print(f"  Frontend → http://localhost:5173")
print(f"  Login    → arun@freshmart.com / password123\n")
sys.exit(0 if FAIL == 0 else 1)
