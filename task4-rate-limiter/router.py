import asyncio
import httpx
from quart import Quart, request, jsonify
from rate_limiter import init_db, check_rate_limit, record_usage, MAX_TOKENS_PER_MINUTE

app = Quart(__name__)

PRIMARY_URL = "http://127.0.0.1:9002/primary/v1/completions"
SECONDARY_URL = "http://127.0.0.1:9002/secondary/v1/completions"
TIMEOUT = 3.0


@app.before_serving
async def startup():
    await init_db()


async def call_model(client: httpx.AsyncClient, url: str, body: dict) -> httpx.Response:
    return await asyncio.wait_for(
        client.post(url, json=body),
        timeout=TIMEOUT,
    )


@app.route("/v1/completions", methods=["POST"])
async def completions():
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({"error": {"code": "AUTH_REQUIRED", "message": "Missing X-API-Key header"}}), 401

    allowed, used = await check_rate_limit(api_key)
    if not allowed:
        return jsonify({"error": {"code": "RATE_LIMITED", "message": f"Token limit exceeded. Used {used}/{MAX_TOKENS_PER_MINUTE} in current window."}}), 429

    body = await request.get_json()

    async with httpx.AsyncClient() as client:
        try:
            resp = await call_model(client, PRIMARY_URL, body)
            if resp.status_code == 429:
                raise httpx.HTTPStatusError("rate limited", request=resp.request, response=resp)
            data = resp.json()
            tokens = data.get("usage", {}).get("total_tokens", 0)
            await record_usage(api_key, tokens)
            return jsonify(data)

        except (httpx.HTTPStatusError, asyncio.TimeoutError, httpx.ConnectError):
            pass

        try:
            resp = await call_model(client, SECONDARY_URL, body)
            data = resp.json()
            data["_fallback"] = True
            tokens = data.get("usage", {}).get("total_tokens", 0)
            await record_usage(api_key, tokens)
            return jsonify(data)

        except Exception:
            return jsonify({"error": {"code": "SERVICE_UNAVAILABLE", "message": "All model providers are unavailable"}}), 503


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8002)