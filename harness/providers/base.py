"""
Abstract base provider interface.

All providers must implement the `complete()` method and return a
normalized response dict. This keeps the orchestrator provider-agnostic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolDefinition:
    """Provider-agnostic tool/function definition."""
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema object


@dataclass
class Message:
    """
    A single conversation message, compatible with all providers.

    role:
      - "user"       : user input
      - "assistant"  : model output
      - "system"     : system prompt (rarely used in message list; usually separate)
      - "tool"       : tool result (native mode only)

    For native tool use:
      - assistant message may carry `tool_calls` list
      - tool result message carries `tool_call_id` and `tool_name`

    `raw_content` optionally holds the provider's native content blocks for an
    assistant turn (e.g. Anthropic thinking/tool_use blocks). When present it is
    replayed verbatim, which is required to preserve signed extended-thinking
    blocks across tool-use turns.
    """
    role: str
    content: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_call_id: str | None = None
    tool_name: str | None = None
    raw_content: list[dict[str, Any]] | None = None


class BaseProvider(ABC):
    """Abstract provider interface. All providers must implement `complete`."""

    @abstractmethod
    async def complete(
        self,
        model: str,
        messages: list[Message],
        system: str = "",
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        thinking: dict | None = None,
    ) -> dict[str, Any]:
        """
        Run inference and return a normalized response dict:

        {
          "text": str,          # Full text content of the response
          "tool_calls": [       # List of tool calls (empty if none)
            {
              "id": str | None,
              "name": str,
              "arguments": dict,
            }
          ],
          "stop_reason": str,   # "end_turn" | "tool_use" | "max_tokens" | ...
          "usage": {            # Token counts (provider-specific keys)
            "input_tokens": int,
            "output_tokens": int,
          },
          "raw": Any,           # Raw provider response object
        }
        """
        ...
