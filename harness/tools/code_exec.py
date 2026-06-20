"""
Sandboxed Python code execution tool.

Runs Python in a subprocess with:
  - Configurable timeout (default 30s, max 60s)
  - Output capture (stdout + stderr)
  - Memory limit via resource module (Linux only, gracefully skipped on other OS)
  - No network access restriction (trust model: brain controls what gets executed)

The subprocess inherits the current virtualenv/PATH so standard libraries
and installed packages are available.
"""

import asyncio
import logging
import sys
import textwrap
from typing import Any

logger = logging.getLogger(__name__)

MAX_OUTPUT_CHARS = 10_000  # Truncate output to prevent context explosion
MAX_TIMEOUT = 60


async def python_exec_handler(args: dict[str, Any]) -> str:
    """
    Execute Python code in a sandboxed subprocess.

    Args:
        code: Python code to run
        timeout: Execution timeout in seconds (default 30, max 60)
    """
    code: str = args.get("code", "")
    timeout: int = min(int(args.get("timeout", 30)), MAX_TIMEOUT)

    if not code:
        return "Error: 'code' argument is required"

    logger.debug("python_exec: timeout=%ds, code_len=%d", timeout, len(code))

    # Wrap the code to set memory limits on Linux
    wrapper = _build_wrapper(code)

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-c", wrapper,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return f"Execution timed out after {timeout} seconds."
    except Exception as exc:
        return f"Failed to launch subprocess: {type(exc).__name__}: {exc}"

    stdout = stdout_bytes.decode("utf-8", errors="replace")
    stderr = stderr_bytes.decode("utf-8", errors="replace")
    returncode = proc.returncode

    return _format_result(stdout, stderr, returncode)


def _build_wrapper(code: str) -> str:
    """
    Wrap user code to:
    1. Set resource limits (Linux only)
    2. Run the actual code
    """
    setup = textwrap.dedent("""\
        import sys, os
        try:
            import resource
            # Limit memory to 512 MB
            resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
        except (ImportError, ValueError):
            pass  # Not on Linux or limit not supported

    """)
    return setup + code


def _format_result(stdout: str, stderr: str, returncode: int) -> str:
    """Format the subprocess result for display."""
    parts = []

    if stdout:
        stdout_trimmed = _truncate(stdout, MAX_OUTPUT_CHARS // 2)
        parts.append(f"stdout:\n{stdout_trimmed}")

    if stderr:
        stderr_trimmed = _truncate(stderr, MAX_OUTPUT_CHARS // 2)
        parts.append(f"stderr:\n{stderr_trimmed}")

    if not stdout and not stderr:
        parts.append("(no output)")

    parts.append(f"exit code: {returncode}")

    return "\n\n".join(parts)


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n[...truncated {len(text) - max_chars} more characters]"
