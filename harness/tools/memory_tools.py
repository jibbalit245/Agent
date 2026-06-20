"""
Memory tools: memory_save and memory_load.

These allow the agent to persist information across conversation turns
and even across sessions. Data is stored per-session in JSON files.
"""

import logging
from pathlib import Path

from harness.tools.registry import registry
from harness.memory.store import get_store

logger = logging.getLogger(__name__)

# Session ID used when no explicit session context is available
_DEFAULT_SESSION = "default"
_current_session_id: str = _DEFAULT_SESSION
_memory_dir: Path = Path("./memory")


def set_session_context(session_id: str, memory_dir: Path | None = None) -> None:
    """
    Set the active session ID for memory operations.

    Called by the gateway layer when a new conversation session begins,
    so memory_save/memory_load operate on the right session's store.
    """
    global _current_session_id, _memory_dir
    _current_session_id = str(session_id)
    if memory_dir is not None:
        _memory_dir = memory_dir
    logger.debug("Memory session set to: %s (dir: %s)", session_id, _memory_dir)


@registry.register(
    name="memory_save",
    description=(
        "Save a piece of information to persistent memory for later recall. "
        "Use this to remember facts, user preferences, or important context "
        "that may be needed in future conversations."
    ),
    parameters={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "A short descriptive key for this memory (e.g. 'user_name', 'project_goal')",
            },
            "value": {
                "type": "string",
                "description": "The information to store",
            },
        },
        "required": ["key", "value"],
    },
)
async def memory_save(key: str, value: str) -> str:
    """Save a key-value pair to persistent memory."""
    store = get_store(_current_session_id, _memory_dir)
    store.save(key, value)
    logger.info("memory_save: session=%s key=%r", _current_session_id, key)
    return f"Saved to memory: {key!r} = {value!r}"


@registry.register(
    name="memory_load",
    description=(
        "Load a previously saved piece of information from memory by key. "
        "Returns the stored value, or a message if the key is not found. "
        "Use memory_load at the start of conversations to recall user context."
    ),
    parameters={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "The key to look up. Use 'list' to see all available keys.",
            },
        },
        "required": ["key"],
    },
)
async def memory_load(key: str) -> str:
    """Load a value from memory, or list all keys."""
    store = get_store(_current_session_id, _memory_dir)

    if key.lower() == "list":
        keys = store.list_keys()
        if not keys:
            return "Memory is empty — no keys stored yet."
        return "Stored memory keys:\n" + "\n".join(f"  - {k}" for k in keys)

    value = store.load(key)
    if value is None:
        keys = store.list_keys()
        hint = f"\nAvailable keys: {', '.join(keys)}" if keys else ""
        return f"No memory found for key: {key!r}{hint}"

    return f"Memory[{key!r}] = {value}"
