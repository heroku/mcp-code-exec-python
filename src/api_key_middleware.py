from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
# local:
from src import config

API_KEY = config.get_env_variable("API_KEY")

# MCP is still working on ironing out SSE authentication protocols, so for now we'll build our own middleware layer:
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