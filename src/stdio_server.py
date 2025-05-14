"""
Runs the server in STDIO mode.

Note: This file doesn't need to be referenced in the Procfile, because STDIO mode doesn't spin up any kind of
long-running server. Instead, it boots up and runs once per request conversation initialization.
"""
import asyncio
import logging
import traceback

from src.set_up_tools import set_up_tools_server

mcp_server = set_up_tools_server()

if __name__ == "__main__":
    logging.info("Starting MCP STDIO server")
    try:
        mcp_server.run(transport="stdio")
    except asyncio.CancelledError:
        logging.info("MCP STDIO server shutdown gracefully.")
    except Exception:
        logging.error("Unexpected error in STDIO transport:")
        traceback.print_exc()
