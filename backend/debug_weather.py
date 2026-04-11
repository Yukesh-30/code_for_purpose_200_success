import urllib.request, json

BASE = "http://127.0.0.1:5000"
with urllib.request.urlopen(urllib.request.Request(BASE+"/auth/login",
    data=json.dumps({"email":"arun@freshmart.com","password":"password123"}).encode(),
    headers={"Content-Type":"application/json"}, method="POST"), timeout=10) as r:
    TOKEN = json.loads(r.read())["access_token"]
    BID = json.loads(r.read())["business_id"] if False else 1

req = urllib.request.Request(BASE+"/chat",
    data=json.dumps({"business_id": BID, "question": "what is the weather today", "include_sql": False}).encode(),
    headers={"Content-Type":"application/json","Authorization":f"Bearer {TOKEN}"},
    method="POST")
with urllib.request.urlopen(req, timeout=15) as r:
    d = json.loads(r.read())
    print(f"status={d.get('status')}  intent={d.get('intent')}")
    print(f"answer={d.get('answer','')[:100]}")
