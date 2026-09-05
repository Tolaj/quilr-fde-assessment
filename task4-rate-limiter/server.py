# Mock Models
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

request_count = 0

# ---------- routes ---------------
@app.route("/primary/v1/completions", methods=["POST"])
def primary():
    global request_count
    request_count += 1

    # Every 3rd request returns 429
    if request_count % 3 == 0:
        return jsonify({"error": "rate limited"}), 429

    # Simulate slow response on every 5th request (will trigger timeout)
    if request_count % 5 == 0:
        time.sleep(5)

    body = request.get_json()
    return jsonify({
        "model": "primary-model",
        "choices": [{"text": f"Primary response to: {body.get('prompt', '')}"}],
        "usage": {"total_tokens": 150},
    })


@app.route("/secondary/v1/completions", methods=["POST"])
def secondary():
    body = request.get_json()
    return jsonify({
        "model": "secondary-model",
        "choices": [{"text": f"Secondary response to: {body.get('prompt', '')}"}],
        "usage": {"total_tokens": 120},
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9002)