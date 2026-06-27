"""
Brain interface — unified layer over model providers.

All supported providers (Anthropic, OpenAI, Moonshot/Kimi) support native
API tool calling, so the Brain runs a single path: it sends tool definitions
to the provider and handles structured tool_use responses.

The Brain object is configured once at startup and reused across requests.
"""

import logging
from typing import Any

from harness.providers.base import BaseProvider, Message, ToolDefinition

logger = logging.getLogger(__name__)


class Brain:
    """
    Wraps a provider and executes one round of native tool-calling inference.

    Sends tool definitions to the provider API and returns structured
    tool_use responses normalized into a common shape.
    """

    def __init__(
        self,
        provider: BaseProvider,
        model: str,
        mode: str = "native",
        system_prompt: str = "",
        thinking: dict | None = None,
    ) -> None:
        # `mode` is accepted for backward compatibility with existing agent
        # configs, but only native tool calling is supported now.
        if mode and mode != "native":
            logger.debug("Brain mode %r ignored — only native tool calling is supported", mode)
        self.provider = provider
        self.model = model
        self.mode = "native"
        self.system_prompt = system_prompt
        # thinking config: {"enabled": bool, "budget_tokens": int, "effort": str}
        self.thinking: dict = thinking or {}

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """
        Run one inference pass.

        Returns a dict with:
          {
            "text": str,                  # final text content (may be empty)
            "tool_calls": [               # list of tool invocations requested
              {"name": str, "arguments": dict, "id": str | None}
            ],
            "stop_reason": str,           # "end_turn" | "tool_use" | "max_tokens" | ...
            "raw_content": list | None,   # provider-native blocks (signed thinking, etc.)
            "raw": Any,                   # raw provider response
          }
        """
        tools = tools or []
        return await self.provider.complete(
            model=self.model,
            messages=messages,
            system=self.system_prompt,
            tools=tools if tools else None,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking=self.thinking or None,
        )

    def build_tool_result_message(
        self,
        tool_name: str,
        tool_id: str | None,
        result: str,
        original_text: str = "",
    ) -> Message:
        """Build the message that carries a tool result back to the model."""
        return Message(
            role="tool",
            content=result,
            tool_call_id=tool_id,
            tool_name=tool_name,
        )
