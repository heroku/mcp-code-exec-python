"""Spins up a test client to interact with MCP server in stdio-mode."""
import asyncio
import json
import sys
import os
from mando import command, main
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Set up how to start your server
server_params = StdioServerParameters(
    command="python",
    args=["-m", "src.stdio_server"],
    # NOTE: you may want to change this depending on what ENV variables you want your LLM to have access to!
    env=os.environ.copy(),
)

async def run(method_name: str, raw_args: str = None):
    """Generalized runner for MCP client methods over stdio."""
    try:
        args = json.loads(raw_args) if raw_args else {}
    except json.JSONDecodeError:
        raise ValueError(f"Could not parse JSON args: {raw_args}")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            method = getattr(session, method_name)
            return await method(**args)


@command
def mcp(method_name, args=None):
    """Call an MCP method by name with optional JSON args (stdio transport).

    Examples:
        This will only work locally:

            python example_clients/test_stdio.py mcp list_tools
            python example_clients/test_stdio.py mcp call_tool --args '{"name": "code_exec_python", "arguments": {"code": "print(list(range(10)))"}}'

        To run against your deployed code:

            heroku run --app $APP_NAME -- bash -c 'python -m example_clients.test_stdio mcp list_tools'
            
            json='{"name": "code_exec_python", "arguments": {"code": "print(list(range(10)))"}}'
            heroku run --app "$APP_NAME" -- bash -c "python -m example_clients.test_stdio mcp call_tool --args '$json'"

        Or simulate a raw STDIO client:

            heroku run --app "$APP_NAME" -- bash -c "python -m src.stdio_server 2> logs.txt" <<EOF

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}

{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}

{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"code_exec_python","arguments":{"code":"import numpy as np; print(np.random.rand(50).tolist())","packages":["numpy"]}}}
EOF

        Soon, you'll also be able to connect up your MPC repo to Heroku's MCP Gateway, which will make streaming from one-off dynos simple!
    """
    result = asyncio.run(run(method_name, args))
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__" and not hasattr(sys, "ps1"):
    main()
