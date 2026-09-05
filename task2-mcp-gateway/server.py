# Mock MCP Server
from flask import Flask, request, jsonify

app = Flask(__name__)

# --------- routes -------------
@app.route("/mcp", methods=["POST"])
def handle_rpc():
    req = request.get_json()

    if req["method"] == "tools/list":
        return jsonify({
            "jsonrpc": "2.0",
            "id": req.get("id"),
            "result": {
                "tools": [
                    {"name": "get_status", "description": "Get system status"},
                    {"name": "admin_reset_key", "description": "Reset an API key (admin only)"},
                    {"name": "admin_delete_user", "description": "Delete a user (admin only)"},
                ]
            },
        })

    if req["method"] == "tools/call":
        return jsonify({
            "jsonrpc": "2.0",
            "id": req.get("id"),
            "result": {"output": f"Tool '{req['params']['name']}' executed successfully"},
        })

    return jsonify({
        "jsonrpc": "2.0",
        "id": req.get("id"),
        "error": {"code": -32601, "message": "Method not found"},
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000)