"""Spins up a test client to interact with MCP server in SSE-mode."""
import os
import asyncio
import json
import sys
from mando import command, main
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

API_KEY=os.environ.get('API_KEY')
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000").rstrip("/") + '/mcp/'

async def run(method_name: str, raw_args: str = None):
    """Generalized runner for MCP client methods."""
    try:
        args = json.loads(raw_args) if raw_args else {}
    except json.JSONDecodeError:
        raise ValueError(f"Could not parse JSON args: {raw_args}")

    headers = {"Authorization": f"Bearer {API_KEY}"}

    async with streamablehttp_client(MCP_SERVER_URL, headers=headers) as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            method = getattr(session, method_name)
            return await method(**args)


@command
def mcp(method_name, args=None):
    result = asyncio.run(run(method_name, args))
    print(json.dumps(result.model_dump(), indent=2))

if __name__ == "__main__" and not hasattr(sys, "ps1"):
    main()
