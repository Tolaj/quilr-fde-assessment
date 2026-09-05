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