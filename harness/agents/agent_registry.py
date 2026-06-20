"""
AgentRegistry — load, save, list, and delete agent configs from disk.

Agent configs live in two places:
  1. agent_configs/defaults/  — built-in agents (read-only, loaded at startup)
  2. agent_configs/           — user-created agents (read/write)

When an ID collision occurs between defaults and user configs, the user
config takes precedence.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from harness.agents.agent_config import AgentConfig

logger = logging.getLogger(__name__)

_DEFAULT_CONFIGS_DIR = Path("agent_configs")
_DEFAULTS_SUBDIR = "defaults"


class AgentRegistry:
    """
    Manages persisted AgentConfig objects on disk.

    The registry loads all configs at instantiation and keeps an in-memory
    index. Mutations (save/delete) are immediately written to disk.
    """

    def __init__(self, configs_dir: Path = _DEFAULT_CONFIGS_DIR) -> None:
        self.configs_dir = configs_dir
        self.defaults_dir = configs_dir / _DEFAULTS_SUBDIR
        self._agents: dict[str, AgentConfig] = {}
        self._load_all()

    # ------------------------------------------------------------------
    # Internal loaders
    # ------------------------------------------------------------------

    def _load_all(self) -> None:
        """Load defaults first, then user configs (user configs win on collision)."""
        # Load built-in defaults
        if self.defaults_dir.exists():
            for path in sorted(self.defaults_dir.glob("*.json")):
                config = self._load_file(path)
                if config:
                    self._agents[config.id] = config
                    logger.debug("Loaded default agent: %s", config.id)

        # Load user configs (overrides defaults)
        if self.configs_dir.exists():
            for path in sorted(self.configs_dir.glob("*.json")):
                config = self._load_file(path)
                if config:
                    self._agents[config.id] = config
                    logger.debug("Loaded user agent: %s", config.id)

        logger.info("AgentRegistry loaded %d agent(s)", len(self._agents))

    def _load_file(self, path: Path) -> Optional[AgentConfig]:
        """Load and parse a single JSON config file. Returns None on error."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AgentConfig.from_dict(data)
        except Exception as exc:
            logger.warning("Failed to load agent config %s: %s", path, exc)
            return None

    def _user_path(self, agent_id: str) -> Path:
        """Return the file path for a user-created agent config."""
        safe_id = agent_id.replace("/", "_").replace("..", "_")
        return self.configs_dir / f"{safe_id}.json"

    def _is_default(self, agent_id: str) -> bool:
        """Return True if this agent's config lives in the defaults directory."""
        return (self.defaults_dir / f"{agent_id}.json").exists()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_agents(self) -> list[AgentConfig]:
        """Return all agents sorted by name."""
        return sorted(self._agents.values(), key=lambda a: a.name.lower())

    def get(self, agent_id: str) -> Optional[AgentConfig]:
        """Return the agent config with the given ID, or None."""
        return self._agents.get(agent_id)

    def get_by_name(self, name: str) -> Optional[AgentConfig]:
        """Look up an agent by display name (case-insensitive)."""
        name_lower = name.lower()
        for agent in self._agents.values():
            if agent.name.lower() == name_lower:
                return agent
        return None

    def find(self, query: str) -> Optional[AgentConfig]:
        """
        Find an agent by ID or name.

        Tries exact ID match first, then case-insensitive name match.
        """
        return self._agents.get(query) or self.get_by_name(query)

    def save(self, config: AgentConfig) -> None:
        """
        Persist an agent config to disk and update the in-memory index.

        Always saves to the user configs directory (not defaults).
        """
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        path = self._user_path(config.id)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            self._agents[config.id] = config
            logger.info("Saved agent config: %s -> %s", config.id, path)
        except Exception as exc:
            logger.error("Failed to save agent config %s: %s", config.id, exc)
            raise

    def delete(self, agent_id: str) -> bool:
        """
        Delete a user-created agent config.

        Returns False if the agent doesn't exist or is a built-in default
        (defaults cannot be deleted, only overridden).
        """
        if agent_id not in self._agents:
            return False
        if self._is_default(agent_id):
            logger.warning("Attempted to delete built-in agent: %s (not allowed)", agent_id)
            return False

        path = self._user_path(agent_id)
        try:
            if path.exists():
                path.unlink()
            del self._agents[agent_id]
            # If a default exists for this ID, it's now visible again
            default_path = self.defaults_dir / f"{agent_id}.json"
            if default_path.exists():
                config = self._load_file(default_path)
                if config:
                    self._agents[config.id] = config
            logger.info("Deleted agent: %s", agent_id)
            return True
        except Exception as exc:
            logger.error("Failed to delete agent %s: %s", agent_id, exc)
            return False

    def exists(self, agent_id: str) -> bool:
        """Return True if an agent with this ID is registered."""
        return agent_id in self._agents

    def count(self) -> int:
        """Return the total number of registered agents."""
        return len(self._agents)

    def reload(self) -> None:
        """Reload all configs from disk (useful after external edits)."""
        self._agents.clear()
        self._load_all()
