"""
Persistent memory store using JSON files.

One JSON file per user, stored in the configured memory directory.
Supports save, load, and list operations.

File format: {key: value, key2: value2, ...}
"""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)

# Lock per user file to prevent concurrent write corruption
_file_locks: dict[str, asyncio.Lock] = {}


def _get_lock(path: str) -> asyncio.Lock:
    if path not in _file_locks:
        _file_locks[path] = asyncio.Lock()
    return _file_locks[path]


def _safe_user_id(user_id: str) -> str:
    """Sanitize user_id to be safe as a filename."""
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", str(user_id))


def make_memory_handlers(
    memory_dir: str = "./memory",
) -> tuple[Callable[[dict[str, Any]], Awaitable[str]], Callable[[dict[str, Any]], Awaitable[str]]]:
    """
    Factory that creates memory_save and memory_load handlers
    bound to the given memory directory.

    Returns (memory_save_handler, memory_load_handler).
    """
    base_dir = Path(memory_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    async def memory_save(args: dict[str, Any]) -> str:
        user_id: str = str(args.get("user_id", "default"))
        key: str = str(args.get("key", ""))
        value: str = str(args.get("value", ""))

        if not key:
            return "Error: 'key' argument is required"

        safe_id = _safe_user_id(user_id)
        file_path = base_dir / f"{safe_id}.json"
        lock = _get_lock(str(file_path))

        async with lock:
            data = _load_file(file_path)
            data[key] = value
            _save_file(file_path, data)

        logger.debug("memory_save: user=%s, key=%r", user_id, key)
        return f"Saved: {key!r} for user {user_id}"

    async def memory_load(args: dict[str, Any]) -> str:
        user_id: str = str(args.get("user_id", "default"))
        key: str | None = args.get("key")

        safe_id = _safe_user_id(user_id)
        file_path = base_dir / f"{safe_id}.json"
        lock = _get_lock(str(file_path))

        async with lock:
            data = _load_file(file_path)

        if key is None:
            # List all keys
            if not data:
                return f"No memories stored for user {user_id}"
            keys = ", ".join(data.keys())
            return f"Stored keys for user {user_id}: {keys}"

        if key not in data:
            return f"No memory found for key {key!r} (user {user_id})"

        logger.debug("memory_load: user=%s, key=%r", user_id, key)
        return f"{key}: {data[key]}"

    return memory_save, memory_load


def _load_file(path: Path) -> dict[str, Any]:
    """Load JSON memory file, returning empty dict if missing or corrupt."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load memory file %s: %s", path, exc)
        return {}


def _save_file(path: Path, data: dict[str, Any]) -> None:
    """Atomically write JSON memory file."""
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp_path.replace(path)
