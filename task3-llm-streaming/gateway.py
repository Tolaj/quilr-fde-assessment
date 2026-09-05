import re
import httpx
from quart import Quart, Response, request

app = Quart(__name__)

LLM_URL = "http://127.0.0.1:9001/v1/completions"

# ---------- email, SSN, credit card ---------------
PII_PATTERNS = re.compile(
    r"(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)"   
    r"|(\b\d{3}-\d{2}-\d{4}\b)"    
    r"|(\b\d{4}-\d{4}-\d{4}-\d{4}\b)"                            
)

MIN_KEEP = 25


@app.route("/v1/completions", methods=["POST"])
async def proxy():
    body = await request.get_json(silent=True) or {}

    async def generate():
        buffer = ""

        async with httpx.AsyncClient() as client:
            async with client.stream("POST", LLM_URL, json=body) as resp:
                async for chunk in resp.aiter_text():
                    buffer += chunk

                    if len(buffer) > MIN_KEEP * 2:
                        split_at = buffer[:-MIN_KEEP].rfind(" ")
                        if split_at > 0:
                            to_flush = buffer[:split_at + 1]
                            buffer = buffer[split_at + 1:]
                            yield PII_PATTERNS.sub("[REDACTED]", to_flush)

        if buffer:
            yield PII_PATTERNS.sub("[REDACTED]", buffer)

    return Response(generate(), content_type="text/plain")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001)
    