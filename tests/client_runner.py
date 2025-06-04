"""
Launch one of the example_clients in a fresh subprocess and return STDOUT.
"""
from __future__ import annotations
import asyncio, os, sys, subprocess, textwrap
from pathlib import Path
from typing import Sequence, Mapping

ROOT      = Path(__file__).resolve().parents[1]
EXAMPLES  = ROOT / "example_clients"
PYTHON_EXE = sys.executable


async def call_client(
    module_name: str,
    cli_args: Sequence[str],
    extra_env: Mapping[str, str] | None = None,
) -> str:
    env = os.environ.copy() | (extra_env or {})

    # ----- NEW: run STDIO client inside a Heroku one-off dyno ----------
    if module_name == "remote_stdio":
        app = env.get("APP_NAME")
        if not app:
            raise RuntimeError("APP_NAME env-var required for remote_stdio context")
        cmd = [
            "heroku", "run", "--exit-code", "--app", app, "--",
            "python", "-m", "example_clients.stdio_client", "mcp", *cli_args,
        ]
    # -------------------------------------------------------------------
    else:
        cmd = [
            PYTHON_EXE,
            "-m", f"example_clients.{module_name}",
            "mcp", *cli_args,
        ]

    proc = await asyncio.create_subprocess_exec(
        *cmd, cwd=ROOT, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out_b, err_b = await proc.communicate()
    out, err = out_b.decode(), err_b.decode()
    if proc.returncode:
        raise RuntimeError(
            textwrap.dedent(
                f"""
                Client {module_name} exited with {proc.returncode}
                CMD   : {' '.join(cmd)}
                STDERR:
                {err}"""
            )
        )
    return out
