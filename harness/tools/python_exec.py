"""
python_exec tool — execute Python code in a sandboxed subprocess.

Runs code in an isolated process with a timeout. Captures stdout/stderr.
NOT a full sandbox (no container isolation), but limited by timeout and
by not importing os-level destructive operations in the tool's own process.
"""

import asyncio
import logging
import sys
import textwrap

from harness.tools.registry import registry

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 30
_MAX_OUTPUT_CHARS = 6000


@registry.register(
    name="python_exec",
    description=(
        "Execute Python code and return stdout/stderr output. "
        "Useful for calculations, data analysis, string manipulation, "
        "and verifying logic. Code runs in an isolated subprocess."
    ),
    parameters={
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute. Use print() to output results.",
            },
            "timeout": {
                "type": "integer",
                "description": f"Execution timeout in seconds (default {_TIMEOUT_SECONDS}, max 60)",
                "default": _TIMEOUT_SECONDS,
            },
        },
        "required": ["code"],
    },
)
async def python_exec(code: str, timeout: int = _TIMEOUT_SECONDS) -> str:
    """Execute Python code in a subprocess and return output."""
    timeout = min(int(timeout), 60)
    logger.info("python_exec: running %d chars of code (timeout=%ds)", len(code), timeout)

    # Wrap in a runner that captures both print output and expression results
    wrapper = textwrap.dedent(f"""\
        import sys, traceback

        _code = {repr(code)}

        try:
            _result = None
            exec(compile(_code, "<agent_code>", "exec"), {{"__builtins__": __builtins__}})
        except SystemExit:
            pass
        except Exception:
            traceback.print_exc()
    """)

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-c", wrapper,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return f"Execution timed out after {timeout} seconds."
    except Exception as exc:
        logger.error("python_exec subprocess failed: %s", exc)
        return f"Failed to execute code: {exc}"

    output_parts = []
    if stdout:
        output_parts.append(stdout.decode(errors="replace"))
    if stderr:
        stderr_text = stderr.decode(errors="replace")
        if stderr_text.strip():
            output_parts.append(f"[stderr]\n{stderr_text}")

    if proc.returncode and proc.returncode != 0:
        output_parts.append(f"[exit code: {proc.returncode}]")

    output = "\n".join(output_parts).strip()

    if not output:
        output = "(no output)"

    if len(output) > _MAX_OUTPUT_CHARS:
        output = output[:_MAX_OUTPUT_CHARS] + f"\n[...truncated at {_MAX_OUTPUT_CHARS} chars]"

    return output
