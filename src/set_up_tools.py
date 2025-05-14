"""
This module registers this repo's tools with FastMCP and creates a server object. It does not run the server.

We could have placed the ability to run both the stdio and SSE servers in this module, but we've chosen to
split them into two separate modules — `sse_server.py` and `stdio_server.py` — for improved code clarity and
so that the FastAPI SSE app can live in the global namespace. This enables `uvicorn` to run with `--reload`.
"""
# File: src/set_up_tools.py
import sys
import logging
from mcp.server.fastmcp import FastMCP

# Local:
from src.code_execution import code_exec_python
from src import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stderr)
logger = logging.getLogger(__name__)

def set_up_tools_server():
    tools = {}
    if (not config.STDIO_MODE_ONLY) or config.is_one_off_dyno:
        tools["code_exec_python"] = code_exec_python

    # Enable streamable HTTP mode
    mcp_server = FastMCP("StatelessServer", stateless_http=True)
    for name, tool in tools.items():
        mcp_server.tool(name=name)(tool)

    return mcp_server
