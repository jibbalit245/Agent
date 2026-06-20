"""
AgentConfig — the data model for a custom agent definition.

Each agent has a unique ID, a persona (system prompt), a model assignment,
a subset of enabled tools, and metadata. Configs are serialized to/from JSON.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(name: str) -> str:
    """Convert a display name to a safe lowercase ID slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\-_]", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug.strip("-") or "agent"


# All tools that agents can be granted access to
ALL_TOOLS = [
    "knowledge_search",
    "web_search",
    "web_fetch",
    "python_exec",
    "memory_save",
    "memory_load",
    "summarize",
]


@dataclass
class AgentConfig:
    """
    Represents a fully-specified custom agent.

    Fields:
      id            — URL-safe unique identifier (derived from name on creation)
      name          — Human-readable display name
      description   — Short description shown in /agents list
      model         — Model ID string (e.g. "claude-sonnet-4-6")
      provider      — Provider name ("anthropic" | "openrouter")
      brain_mode    — Inference mode ("native" | "tags")
      system_prompt — Full system prompt / persona for this agent
      tools         — List of tool names this agent is allowed to use
      temperature   — Sampling temperature (0.0–1.0)
      created_at    — ISO 8601 creation timestamp
      updated_at    — ISO 8601 last-modified timestamp
    """

    id: str
    name: str
    description: str = ""
    model: str = "claude-sonnet-4-6"
    provider: str = "anthropic"
    brain_mode: str = "native"
    system_prompt: str = "You are a helpful AI assistant."
    tools: list[str] = field(default_factory=lambda: list(ALL_TOOLS))
    temperature: float = 0.7
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    # thinking config — controls extended reasoning depth
    # Claude:     {"enabled": true, "budget_tokens": 8000}   (up to 32000)
    # OpenAI o*:  {"enabled": true, "effort": "high"}        (low/medium/high)
    # DeepSeek:   thinking blocks are always on; this controls stripping them from output
    thinking: dict = field(default_factory=dict)

    # Optional: path to knowledge/context files attached to this agent
    knowledge_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict (ready for json.dump)."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "provider": self.provider,
            "brain_mode": self.brain_mode,
            "system_prompt": self.system_prompt,
            "tools": self.tools,
            "temperature": self.temperature,
            "thinking": self.thinking,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "knowledge_files": self.knowledge_files,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentConfig":
        """Deserialize from a dict (as loaded by json.load)."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            model=data.get("model", "claude-sonnet-4-6"),
            provider=data.get("provider", "anthropic"),
            brain_mode=data.get("brain_mode", "native"),
            system_prompt=data.get("system_prompt", "You are a helpful AI assistant."),
            tools=data.get("tools", list(ALL_TOOLS)),
            temperature=float(data.get("temperature", 0.7)),
            thinking=data.get("thinking", {}),
            created_at=data.get("created_at", _now_iso()),
            updated_at=data.get("updated_at", _now_iso()),
            knowledge_files=data.get("knowledge_files", []),
        )

    @classmethod
    def create(
        cls,
        name: str,
        description: str = "",
        model: str = "claude-sonnet-4-6",
        provider: str = "anthropic",
        brain_mode: str = "native",
        system_prompt: str = "You are a helpful AI assistant.",
        tools: list[str] | None = None,
        temperature: float = 0.7,
        thinking: dict | None = None,
    ) -> "AgentConfig":
        """Factory method — derives ID from name and sets timestamps."""
        agent_id = slugify(name)
        now = _now_iso()
        return cls(
            id=agent_id,
            name=name,
            description=description,
            model=model,
            provider=provider,
            brain_mode=brain_mode,
            system_prompt=system_prompt,
            tools=tools if tools is not None else list(ALL_TOOLS),
            temperature=temperature,
            thinking=thinking or {},
            created_at=now,
            updated_at=now,
        )

    def touch(self) -> None:
        """Update the updated_at timestamp to now."""
        self.updated_at = _now_iso()

    def summary_line(self) -> str:
        """One-line summary for listing."""
        tool_count = len(self.tools)
        return (
            f"*{self.name}* (`{self.id}`)\n"
            f"  {self.description or 'No description'}\n"
            f"  Model: `{self.model}` | Tools: {tool_count} | Temp: {self.temperature}"
        )
