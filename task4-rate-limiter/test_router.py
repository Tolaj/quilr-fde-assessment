import httpx
import sqlite3, time, os

URL = "http://127.0.0.1:8002/v1/completions"
HEADERS = {"X-API-Key": "tenant-123"}

print("--- Test 1: No API key ---")
resp = httpx.post(URL, json={"prompt": "hello"})
print(resp.status_code, resp.json(), "\n")

print("--- Test 2-7: Six requests (primary, primary, fallback-429, primary, fallback-timeout, primary) ---")
for i in range(6):
    resp = httpx.post(URL, json={"prompt": f"request {i+1}"}, headers=HEADERS, timeout=10)
    print(f"Request {i+1}: {resp.status_code} {resp.json()}\n")
    
print("--- Test 8: Rate limit test ---")

conn = sqlite3.connect("rate_limiter.db")
conn.execute("DELETE FROM token_usage WHERE api_key = 'tenant-rate-test'")
conn.commit()
conn.execute(
    "INSERT INTO token_usage (api_key, tokens, timestamp) VALUES (?, ?, ?)",
    ("tenant-rate-test", 49900, time.time()),
)
conn.commit()
conn.close()

HEADERS2 = {"X-API-Key": "tenant-rate-test"}

resp = httpx.post(URL, json={"prompt": "should work"}, headers=HEADERS2, timeout=10)
print(f"Request at 49900 tokens: {resp.status_code} {resp.json()}\n")

resp = httpx.post(URL, json={"prompt": "should fail"}, headers=HEADERS2, timeout=10)
print(f"Request at ~50050 tokens: {resp.status_code} {resp.json()}\n")