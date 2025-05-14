# Long-running (multi-tenant) Streamable HTTP Server (note by default 0 web servers will spin up, to save on costs - see README).
web: uvicorn src.streamable_http_server:app --host=0.0.0.0 --port=${PORT:-8000} --workers=${WEB_CONCURRENCY:-1}

# If you'd prefer to instead run a (deprecated) SSE MCP server, instead use:
# web: uvicorn src.sse_server:app --host=0.0.0.0 --port=${PORT:-8000} --workers=${WEB_CONCURRENCY:-1}

# This is a special Heroku MCP process that we're declaring (optional, but gives you access to some nice features - see https://devcenter.heroku.com/articles/heroku-inference-working-with-mcp)
mcp-python: python -m src.stdio_server
