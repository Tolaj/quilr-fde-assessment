## Task 1: Custom MCP Server

MCP server over stdio transport with two tools and validation using Pydantic.

### Tools
- `get_customer_record` — params(customer ID: `CUST-XXXXX`)
- `trigger_refund` — params(customer ID, positive amount, reason ≥ 10 chars)

### Run
```bash
uv pip install mcp pydantic
python task1-mcp-server/server.py
