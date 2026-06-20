"""
AgentManager — instantiate and run agents from their configs.

The manager creates Brain + Orchestrator instances from an AgentConfig,
and manages per-session conversation history so each active agent session
is stateful.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from harness.agents.agent_config import AgentConfig
from harness.agents.agent_registry import AgentRegistry
from harness.core.brain import Brain
from harness.core.orchestrator import Orchestrator, OrchestratorResult
from harness.providers.base import BaseProvider, Message
from harness.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


@dataclass
class AgentSession:
    """
    Active session for a specific user interacting with a specific agent.

    Holds conversation history and the configured orchestrator.
    """
    session_id: str          # e.g. "telegram_12345678"
    agent_config: AgentConfig
    orchestrator: Orchestrator
    history: list[Message] = field(default_factory=list)
    total_turns: int = 0

    def clear_history(self) -> None:
        """Reset conversation history (start fresh with same agent)."""
        self.history.clear()
        self.total_turns = 0
        logger.info("Cleared history for session %s (agent: %s)", self.session_id, self.agent_config.id)


class AgentManager:
    """
    Creates and manages AgentSession objects.

    A session is identified by (user_session_id, agent_id). Multiple users
    can each have their own active session with different or the same agent.
    """

    def __init__(
        self,
        registry: AgentRegistry,
        tool_registry: ToolRegistry,
        providers: dict[str, BaseProvider],
        default_agent_id: str | None = None,
    ) -> None:
        """
        Args:
            registry:        The AgentRegistry for loading agent configs.
            tool_registry:   The ToolRegistry with all available tools.
            providers:       Dict mapping provider name → BaseProvider instance.
            default_agent_id: Agent to use when no agent is explicitly selected.
        """
        self.registry = registry
        self.tool_registry = tool_registry
        self.providers = providers
        self.default_agent_id = default_agent_id
        self._sessions: dict[str, AgentSession] = {}

    def _session_key(self, user_id: str, agent_id: str) -> str:
        return f"{user_id}::{agent_id}"

    def get_active_agent_id(self, user_id: str) -> str | None:
        """Return the agent ID currently selected for this user."""
        # Sessions are stored with the agent ID embedded in the key.
        # Find any session key that starts with this user's prefix.
        prefix = f"{user_id}::"
        for key in self._sessions:
            if key.startswith(prefix):
                return self._sessions[key].agent_config.id
        return self.default_agent_id

    def get_active_session(self, user_id: str) -> AgentSession | None:
        """Return the currently active session for this user, if any."""
        active_agent_id = self.get_active_agent_id(user_id)
        if active_agent_id is None:
            return None
        key = self._session_key(user_id, active_agent_id)
        return self._sessions.get(key)

    def _make_orchestrator(self, config: AgentConfig) -> Orchestrator:
        """Build a Brain + Orchestrator from an AgentConfig."""
        provider = self.providers.get(config.provider)
        if provider is None:
            # Fall back to first available provider
            if self.providers:
                provider = next(iter(self.providers.values()))
                logger.warning(
                    "Provider %r not available for agent %s, using %s",
                    config.provider, config.id, next(iter(self.providers)),
                )
            else:
                raise RuntimeError("No providers configured")

        brain = Brain(
            provider=provider,
            model=config.model,
            mode=config.brain_mode,
            system_prompt=config.system_prompt,
        )

        # Build a tool sub-registry with only the enabled tools
        # We pass subset to get_definitions but keep the full dispatch
        # capability — the Orchestrator only sends the whitelisted definitions
        # to the model, so it won't call unlisted tools.

        return Orchestrator(
            brain=brain,
            tool_registry=self.tool_registry,
            max_iterations=10,
            system_prompt=config.system_prompt,
            enabled_tools=config.tools,
        )

    def use_agent(self, user_id: str, agent_id: str) -> AgentSession:
        """
        Switch the given user to a specific agent.

        If a session already exists for this (user, agent) pair, it is returned
        (preserving history). Otherwise a new session is created.

        Clears any other active sessions for this user (one active agent per user).
        """
        config = self.registry.get(agent_id)
        if config is None:
            raise ValueError(f"Agent not found: {agent_id!r}")

        # Remove old sessions for this user
        old_keys = [k for k in self._sessions if k.startswith(f"{user_id}::")]
        for k in old_keys:
            del self._sessions[k]

        key = self._session_key(user_id, agent_id)
        if key not in self._sessions:
            orchestrator = self._make_orchestrator(config)
            session = AgentSession(
                session_id=key,
                agent_config=config,
                orchestrator=orchestrator,
            )
            self._sessions[key] = session
            logger.info("Created new session: user=%s agent=%s", user_id, agent_id)
        else:
            session = self._sessions[key]
            logger.info("Resumed existing session: user=%s agent=%s", user_id, agent_id)

        return session

    def ensure_session(self, user_id: str) -> AgentSession:
        """
        Return the active session for this user, creating one with the default
        agent if none exists.
        """
        existing = self.get_active_session(user_id)
        if existing:
            return existing

        agent_id = self.default_agent_id
        if agent_id is None:
            agents = self.registry.list_agents()
            if not agents:
                raise RuntimeError("No agents configured. Use /newagent to create one.")
            agent_id = agents[0].id

        return self.use_agent(user_id, agent_id)

    async def chat(
        self,
        user_id: str,
        message: str,
        temperature: float | None = None,
        max_tokens: int = 4096,
    ) -> OrchestratorResult:
        """
        Send a message to the active agent for this user and return the result.

        Creates a default session if none exists.
        """
        session = self.ensure_session(user_id)
        config = session.agent_config

        result = await session.orchestrator.run(
            user_message=message,
            history=session.history,
            temperature=temperature if temperature is not None else config.temperature,
            max_tokens=max_tokens,
        )

        # Append this turn to the conversation history
        session.history.append(Message(role="user", content=message))
        session.history.append(Message(role="assistant", content=result.text))
        session.total_turns += 1

        return result

    def clear_history(self, user_id: str) -> bool:
        """Clear conversation history for the user's active session."""
        session = self.get_active_session(user_id)
        if session:
            session.clear_history()
            return True
        return False

    def list_user_sessions(self, user_id: str) -> list[AgentSession]:
        """Return all active sessions for a user."""
        prefix = f"{user_id}::"
        return [s for k, s in self._sessions.items() if k.startswith(prefix)]
