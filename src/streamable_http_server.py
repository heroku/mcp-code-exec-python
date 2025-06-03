"""
Runs the MCP server in Streamable HTTP (stateless) mode.

We're using Uvicorn in the Procfile to run the server. While we could use `mcp_server.run()` to achieve
approximately the same result, running Uvicorn directly gives us more flexibility — for example, the ability
to use `--reload`, which is fantastic for fast-iteration during local development.
"""
# Local:
from src.set_up_tools import set_up_tools_server
from src.api_key_middleware import APIKeyMiddleware

mcp_server = set_up_tools_server()
# create a streamable http sub-app:
app = mcp_server.streamable_http_app()
# add optional api key middleware: (vs oauth)
app.add_middleware(APIKeyMiddleware)