"""Spins up a test client to interact with MCP server in SSE-mode."""
import os
import asyncio
import json
import sys
from mando import command, main
from mcp import ClientSession
from mcp.client.sse import sse_client

API_KEY=os.environ.get('API_KEY')
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/") + 'sse'

async def run(method_name: str, raw_args: str = None):
    """Generalized runner for MCP client methods."""
    try:
        args = json.loads(raw_args) if raw_args else {}
    except json.JSONDecodeError:
        raise ValueError(f"Could not parse JSON args: {raw_args}")

    # We'll use this for now until MCP solidifies their authentication recommendations, and the MCP package implements!
    headers = {"Authorization": f"Bearer {API_KEY}"}

    async with sse_client(MCP_SERVER_URL, headers=headers) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            method = getattr(session, method_name)
            return await method(**args)

@command
def mcp(method_name, args=None):
    """Call an MCP method by name with optional JSON args.

    Examples:
        python example_clients/test_sse.py mcp list_tools
        python example_clients/test_sse.py mcp call_tool --args '{"name": "fetch_webpage_and_markdownify", "arguments": {"url": "https://example.com"}}'
    """
    result = asyncio.run(run(method_name, args))
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__" and not hasattr(sys, "ps1"):
    main()
