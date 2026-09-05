import jwt
import httpx

SECRET = "secret-key"

admin_token = jwt.encode({"role": "admin"}, SECRET, algorithm="HS256")
viewer_token = jwt.encode({"role": "viewer"}, SECRET, algorithm="HS256")

GATEWAY = "http://127.0.0.1:8000/mcp"

tests = [
    ("Admin lists tools", admin_token, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}),
    ("Viewer lists tools", viewer_token, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
    ("Admin calls admin tool", admin_token, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "admin_reset_key"}}),
    ("Viewer calls admin tool", viewer_token, {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "admin_reset_key"}}),
    ("Viewer calls normal tool", viewer_token, {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "get_status"}}),
    ("No token", None, {"jsonrpc": "2.0", "id": 6, "method": "tools/list"}),
]

for label, token, body in tests:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = httpx.post(GATEWAY, json=body, headers=headers)
    print(f"{label}: {resp.status_code} {resp.json()}\n")