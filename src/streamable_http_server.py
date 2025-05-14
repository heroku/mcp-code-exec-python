"""
Runs the MCP server in Streamable HTTP mode.

We're using Uvicorn in the Procfile to run the server. Running Uvicorn directly gives us more flexibility,
like using --reload for fast iteration during local development.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from src.set_up_tools import set_up_tools_server
from src import config

API_KEY = config.get_env_variable("API_KEY")

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("authorization")
        api_key_header = request.headers.get("x-api-key")
        token = None

        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header[7:]
        elif api_key_header:
            token = api_key_header

        if token != API_KEY:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

        return await call_next(request)

mcp_server = set_up_tools_server()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp_server.session_manager.run():
        yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(APIKeyMiddleware)

# Mount the MCP streamable HTTP app
# app.mount("/", mcp_server.streamable_http_app())
app.mount("/mcp/", mcp_server.streamable_http_app(), name="mcp")
