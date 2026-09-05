import asyncio, sys, os
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def main():
    params = StdioServerParameters(command=sys.executable, args=[os.path.join(os.path.dirname(__file__), "server.py")])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()
            print(await s.call_tool("get_customer_record", {"customer_id": "CUST-00001"}),"\n")
            print(await s.call_tool("get_customer_record", {"customer_id": "BAD"}),"\n")
            print(await s.call_tool("trigger_refund", {"customer_id": "CUST-00001", "amount": 29.99, "reason": "Item was damaged during shipping"}),"\n")
            print(await s.call_tool("trigger_refund", {"customer_id": "CUST-00001", "amount": -5.0, "reason": "valid reason here"}),"\n")
            print(await s.call_tool("trigger_refund", {"customer_id": "CUST-00001", "amount": 10.0, "reason": "short"}),"\n")

asyncio.run(main())