import jwt
import httpx
from flask import Flask, request, jsonify

app = Flask(__name__)

DOWNSTREAM_URL = "http://127.0.0.1:9000/mcp"
JWT_SECRET = "secret-key"

# --------- utility function ----------
def get_role_from_token(auth_header: str) -> str | None:
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("role")
    except jwt.InvalidTokenError:
        return None

# ------------- routes -------------
@app.route("/mcp", methods=["POST"])
def proxy():
    auth = request.headers.get("Authorization")
    role = get_role_from_token(auth)

    if role is None:
        return jsonify({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": "Missing or invalid authorization token"},
        }), 401

    body = request.get_json()

    if body.get("method") == "tools/call":
        tool_name = body.get("params", {}).get("name", "")
        if tool_name.startswith("admin_") and role != "admin":
            return jsonify({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {"code": -32001, "message": "Unauthorized Tool Call"},
            }), 403

    resp = httpx.post(DOWNSTREAM_URL, json=body)
    return jsonify(resp.json()), resp.status_code


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)