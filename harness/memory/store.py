"""
Simple file-backed memory store.

Each user/agent session gets its own JSON file under the memory directory.
Keys and values are both strings. Simple enough to be auditable and portable.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_MEMORY_DIR = Path("./memory")


class MemoryStore:
    """
    Persistent key-value store backed by a JSON file.

    Thread-safe for single-process use (no file locking needed since
    Python's GIL + asyncio keep single-threaded).
    """

    def __init__(self, store_path: Path) -> None:
        self.store_path = store_path
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load data from disk if the file exists."""
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                logger.debug("Loaded memory from %s (%d keys)", self.store_path, len(self._data))
            except Exception as exc:
                logger.warning("Could not load memory from %s: %s — starting fresh", self.store_path, exc)
                self._data = {}
        else:
            self._data = {}

    def _save(self) -> None:
        """Persist data to disk."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            logger.debug("Saved memory to %s", self.store_path)
        except Exception as exc:
            logger.error("Could not save memory to %s: %s", self.store_path, exc)

    def save(self, key: str, value: str) -> None:
        """Store a value under the given key."""
        self._data[key] = value
        self._save()

    def load(self, key: str) -> str | None:
        """Retrieve a value by key, or None if not found."""
        return self._data.get(key)

    def delete(self, key: str) -> bool:
        """Delete a key. Returns True if it existed."""
        if key in self._data:
            del self._data[key]
            self._save()
            return True
        return False

    def list_keys(self) -> list[str]:
        """Return sorted list of all stored keys."""
        return sorted(self._data.keys())

    def all(self) -> dict[str, Any]:
        """Return a copy of all stored data."""
        return dict(self._data)


# Global store factory — keyed by user/session ID
_stores: dict[str, MemoryStore] = {}


def get_store(session_id: str, base_dir: Path = _DEFAULT_MEMORY_DIR) -> MemoryStore:
    """Get or create a MemoryStore for the given session."""
    if session_id not in _stores:
        safe_id = session_id.replace("/", "_").replace("..", "_")
        path = base_dir / f"{safe_id}.json"
        _stores[session_id] = MemoryStore(path)
    return _stores[session_id]
