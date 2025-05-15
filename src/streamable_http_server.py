"""
Runs the MCP server in Streamable HTTP mode.

We're using Uvicorn in the Procfile to run the server. Running Uvicorn directly gives us more flexibility,
like using --reload for fast iteration during local development.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.responses import JSONResponse
from starlette.datastructures import Headers
# Local:
from src.set_up_tools import set_up_tools_server
from src import config

API_KEY = config.get_env_variable("API_KEY")

class APIKeyASGIMiddleware:
    def __init__(self, app: ASGIApp, header_name: str = "authorization", valid_key: str = ""):
        self.app = app
        self.header_name = header_name.lower()
        self.valid_key = valid_key

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            auth_header = headers.get("authorization") or headers.get("x-api-key")

            # Strip "Bearer " if present
            token = auth_header.replace("Bearer ", "") if auth_header else None

            if token != self.valid_key:
                # Return 401 manually (ASGI style)
                response = JSONResponse({"detail": "Invalid API Key"}, status_code=401)
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


# Putting this in the global namespace so we can optionally run uvicorn with --reload - useful for local development.
mcp_server = set_up_tools_server()
app = FastAPI()
app.add_middleware(APIKeyASGIMiddleware, header_name="X-API-Key", valid_key=API_KEY)
app.mount("/", mcp_server.streamable_http_app(), name="mcp")
