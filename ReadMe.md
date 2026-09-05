## Task 1: Custom MCP Server

MCP server over stdio transport with two tools and validation using Pydantic.

### Tools
- `get_customer_record` — params(customer ID: `CUST-XXXXX`)
- `trigger_refund` — params(customer ID, positive amount, reason ≥ 10 chars)

### Run
```bash
uv pip install mcp pydantic
python task1-mcp-server/server.py
```

## Task 2: MCP Security Gateway Proxy

HTTP/JSON-RPC reverse proxy with Bearer token auth and role-based tool filtering.

### Components
- `gateway.py` — proxy that inspects tokens and filters `admin_` tools
- `server.py` — downstream mock MCP server for testing

### Run
```bash
pip install flask httpx pyjwt
python task2-mcp-gateway/server.py
python task2-mcp-gateway/gateway.py    
python task2-mcp-gateway/test_gateway.py
```

## Task 3: LLM Gateway Streaming Guardrail (PII Redaction)

Async streaming proxy that redacts PII (emails, SSNs, credit cards) from LLM responses in real time.

### Design
- Word-boundary buffer split ensures cross-chunk PII is never cut mid-pattern
- Compiled regex on small chunks, not full response
- Buffer flushes frequently at word boundaries — never accumulates full response

### Components
- `gateway.py` — async Quart proxy with PII redaction
- `server.py` — mock LLM that streams text containing split PII

### Run
```bash
pip install flask quart httpx
python task3-llm-streaming/server.py
python task3-llm-streaming/gateway.py
python task3-llm-streaming/test_gateway.py 
```

## Task 4: Rate-Limiting & Model Fallback Router

Async LLM gateway router with token-aware sliding window rate limiter and automatic model failover.

### Design
- Sliding window rate limiter (50,000 tokens/min per API key) persisted in SQLite
- Primary model 429 or 3s timeout, automatic failover to secondary
- Standardized error payloads, no leaked stack traces

### Components
- `router.py` — async Quart gateway with rate limiting and fallback
- `rate_limiter.py` — sliding window token tracker using aiosqlite
- `server.py` — mock primary (429s + slow responses) and secondary endpoints

### Run
```bash
pip install quart httpx aiosqlite
python task4-rate-limiter/server.py
cd task4-rate-limiter && python router.py
python task4-rate-limiter/test_router.py