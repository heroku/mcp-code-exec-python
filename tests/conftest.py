"""
All transports tested

Contexts yielded:
    • http_local      – streamable HTTP on :8000
    • sse_local       – SSE app on :8000  (same port; we stop the HTTP one first)
    • stdio_local     – client boots its own server
    • remote          – hits your Heroku app (either streamable http or SSE) if MCP_SERVER_URL & API_KEY are set
"""

from __future__ import annotations
import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict

import pytest

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
API_KEY = os.getenv("API_KEY", "local-test-key")
PORT = 8000
WAIT = 25 # seconds


# ---------------------------------------------------------------- helpers
async def _wait_until_up(timeout: int = WAIT) -> None:
    for _ in range(timeout * 4):
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", PORT)
            writer.close(); await writer.wait_closed()
            return
        except OSError:
            await asyncio.sleep(0.25)
    raise RuntimeError("Timed-out waiting for 127.0.0.1:8000")


def _spawn(app_module: str) -> subprocess.Popen[str]:
    """Run uvicorn in its own process pointing at the given module:app."""
    env = os.environ.copy() | {"API_KEY": API_KEY, "PYTHONPATH": str(ROOT)}
    cmd = [PY, "-m", "uvicorn", f"{app_module}:app", "--port", str(PORT), "--no-access-log"]
    return subprocess.Popen(cmd, cwd=ROOT, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


# ---------------------------------------------------------------- local ctx factories
async def _ctx_http_local() -> AsyncGenerator[Dict, None]:
    proc = _spawn("src.streamable_http_server")
    try:
        await _wait_until_up()
        yield {"client": "streamable_http_client",
               "extra_env": {"API_KEY": API_KEY, "MCP_SERVER_URL": f"http://127.0.0.1:{PORT}"}}
    finally:
        proc.terminate(); proc.wait()


async def _ctx_sse_local() -> AsyncGenerator[Dict, None]:
    proc = _spawn("src.sse_server")        # same port; previous proc already gone
    try:
        await _wait_until_up()
        # trailing slash required so client appends “sse” cleanly
        yield {"client": "sse_client",
               "extra_env": {"API_KEY": API_KEY, "MCP_SERVER_URL": f"http://127.0.0.1:{PORT}/"}}
    finally:
        proc.terminate(); proc.wait()


async def _ctx_stdio_local() -> AsyncGenerator[Dict, None]:
    yield {"client": "stdio_client", "extra_env": {}}


# ---------------------------------------------------------------- remote HTTP / SSE
async def _ctx_remote() -> AsyncGenerator[Dict, None]:
    url = os.getenv("MCP_SERVER_URL"); key = os.getenv("API_KEY")
    if not url or not key:
        pytest.skip("remote env-vars missing")
    yield {"client": "streamable_http_client",
           "extra_env": {"API_KEY": key, "MCP_SERVER_URL": url.rstrip("/")}}

# ---------------------------------------------------------------- remote STDIO ctx
async def _ctx_remote_stdio() -> AsyncGenerator[Dict, None]:
    app = os.getenv("APP_NAME"); key = os.getenv("API_KEY")
    if not app or not key:
        pytest.skip("APP_NAME or API_KEY env-var missing for remote stdio")
    # one-off dyno will pick up API_KEY from Heroku config; no MCP_SERVER_URL needed
    yield {"client": "remote_stdio", "extra_env": {"API_KEY": key, "APP_NAME": app}}


CONTEXTS = {
    "http_local":   _ctx_http_local,
    "sse_local":    _ctx_sse_local,
    "stdio_local":  _ctx_stdio_local,
    "remote":       _ctx_remote,
    "remote_stdio": _ctx_remote_stdio,
}

# ---------------------------------------------------------------- public fixture
@pytest.fixture(params=CONTEXTS, ids=list(CONTEXTS))
async def ctx(request):
    async for c in CONTEXTS[request.param]():
        yield c
