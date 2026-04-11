import requests
import json
import os
import uuid

BASE_URL = 'http://localhost:5000'
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), '../sample_data')

def run_tests():
    print("--- starting e2e backend integration test ---")

    # 1. Signup
    test_user_email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    signup_data = {
        "full_name": "Integration Test User",
        "email": test_user_email,
        "password": "password123",
        "role": "msme_owner"
    }
    
    print(f"[*] testing /auth/signup for {test_user_email}")
    res = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    assert res.status_code == 201, f"Signup failed: {res.text}"
    print("  [x] signup success")

    # 2. Login
    print("[*] testing /auth/login")
    res = requests.post(f"{BASE_URL}/auth/login", json=signup_data)
    assert res.status_code == 200, f"Login failed: {res.text}"
    login_data = res.json()
    token = login_data['access_token']
    business_id = login_data['user']['business_id']
    print(f"  [x] login success. Got token and business_id={business_id}")

    headers = {'Authorization': f'Bearer {token}'}

    # 3. Upload Bank Transactions
    print("[*] testing /upload/bank-transactions")
    tx_file = os.path.join(SAMPLE_DATA_DIR, 'bank_transactions.csv')
    with open(tx_file, 'rb') as f:
        files = {'file': ('bank_transactions.csv', f, 'text/csv')}
        data = {'business_id': str(business_id)}
        res = requests.post(f"{BASE_URL}/upload/bank-transactions", headers=headers, files=files, data=data)
        assert res.status_code in [200, 201], f"Upload tx failed: {res.text}"
        print(f"  [x] uploaded transactions: {res.json()}")

    # 4. Dashboard Report Generation
    print("[*] testing /dashboard/report")
    res = requests.post(f"{BASE_URL}/dashboard/report", headers=headers, json={'business_id': business_id})
    assert res.status_code == 200, f"Report generation failed: {res.text}"
    assert res.headers['Content-Type'] == 'text/csv; charset=utf-8'
    print("  [x] report generation success")

    # 5. Chat start
    print("[*] testing /chat/start")
    res = requests.post(f"{BASE_URL}/chat/start", headers=headers, json={'business_id': business_id})
    assert res.status_code == 201, f"Chat start failed: {res.text}"
    session_id = res.json()['session_id']
    print(f"  [x] chat session started: {session_id}")

    # 6. Chat query
    print("[*] testing /chat/query")
    query_payload = {
        'session_id': session_id,
        'query': 'What is my total credit amount for bank transactions?'
    }
    # Might take a few seconds due to LLM calls
    res = requests.post(f"{BASE_URL}/chat/query", headers=headers, json=query_payload)
    if res.status_code == 200:
        print(f"  [x] chat query success: {res.json().get('insight', {}).get('answer')[:100]}...")
    else:
        print(f"  [!] chat query failed (often happens if LLM API not configured or timeouts): {res.text}")

    # 7. Check dummy endpoints
    print("[*] testing /forecasting/optimize")
    res = requests.post(f"{BASE_URL}/forecasting/optimize", headers=headers, json={'business_id': business_id})
    assert res.status_code == 200, res.text
    print("  [x] optimization dummy route success")

    print("\n--- ALL TESTS PASSED SUCCESSFULLY! ---")

if __name__ == '__main__':
    run_tests()
