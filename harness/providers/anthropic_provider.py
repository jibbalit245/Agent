"""
Anthropic Claude provider.

Uses the official anthropic SDK with native tool calling support.
Normalizes responses to the BaseProvider response format.
"""

import json
import logging
from typing import Any

import anthropic

from harness.providers.base import BaseProvider, Message, ToolDefinition

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """
    Provider for Anthropic Claude models.

    Supports:
      - Native tool calling (tool_use content blocks)
      - Streaming (optional, not used here for simplicity)
      - All current Claude models
    """

    def __init__(self, api_key: str) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    def _convert_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        """Convert our Message objects to Anthropic API format."""
        result = []
        for msg in messages:
            if msg.role == "tool":
                # Tool results go as user messages with tool_result content blocks
                result.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg.tool_call_id or "",
                            "content": msg.content,
                        }
                    ],
                })
            elif msg.role == "assistant" and msg.raw_content:
                # Replay the provider's original content blocks verbatim. This
                # preserves signed thinking blocks, which Anthropic requires on
                # any assistant turn that contains tool_use when extended
                # thinking is enabled.
                result.append({"role": "assistant", "content": msg.raw_content})
            elif msg.role == "assistant" and msg.tool_calls:
                # Assistant message with tool calls (no raw blocks available)
                content: list[dict] = []
                if msg.content:
                    content.append({"type": "text", "text": msg.content})
                for tc in msg.tool_calls:
                    content.append({
                        "type": "tool_use",
                        "id": tc.get("id", "call_0"),
                        "name": tc["name"],
                        "input": tc["arguments"] if isinstance(tc["arguments"], dict) else json.loads(tc["arguments"]),
                    })
                result.append({"role": "assistant", "content": content})
            else:
                result.append({"role": msg.role, "content": msg.content})
        return result

    def _convert_tools(self, tools: list[ToolDefinition]) -> list[dict[str, Any]]:
        """Convert ToolDefinition objects to Anthropic tool format."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters,
            }
            for tool in tools
        ]

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
        """Run inference via Anthropic API and return normalized response."""
        api_messages = self._convert_messages(messages)
        api_tools = self._convert_tools(tools) if tools else []

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
        }
        if system:
            kwargs["system"] = system
        if api_tools:
            kwargs["tools"] = api_tools

        # Extended thinking — when enabled, temperature must be 1.0 per Anthropic spec
        thinking_enabled = thinking and thinking.get("enabled")
        if thinking_enabled:
            budget = int(thinking.get("budget_tokens", 8000))
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}
            kwargs["max_tokens"] = max(max_tokens, budget + 1024)
            kwargs["temperature"] = 1.0  # Required when thinking is active
            logger.debug("Extended thinking enabled: budget=%d tokens", budget)
        else:
            kwargs["temperature"] = temperature

        logger.debug(
            "Anthropic request: model=%s, messages=%d, tools=%d, thinking=%s",
            model, len(api_messages), len(api_tools), thinking_enabled,
        )

        response = await self.client.messages.create(**kwargs)

        # Normalize response — collect text, thinking, and tool_use blocks.
        # Also serialize every block into raw_content so it can be replayed
        # verbatim on the next turn (required to keep signed thinking blocks
        # valid across tool use).
        text_parts: list[str] = []
        thinking_parts: list[str] = []
        tool_calls: list[dict] = []
        raw_content: list[dict] = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
                raw_content.append({"type": "text", "text": block.text})
            elif block.type == "thinking":
                thinking_parts.append(getattr(block, "thinking", ""))
                raw_content.append({
                    "type": "thinking",
                    "thinking": getattr(block, "thinking", ""),
                    "signature": getattr(block, "signature", ""),
                })
            elif block.type == "redacted_thinking":
                raw_content.append({
                    "type": "redacted_thinking",
                    "data": getattr(block, "data", ""),
                })
            elif block.type == "tool_use":
                arguments = block.input if isinstance(block.input, dict) else json.loads(block.input)
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": arguments,
                })
                raw_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": arguments,
                })

        stop_reason_map = {
            "end_turn": "end_turn",
            "tool_use": "tool_use",
            "max_tokens": "max_tokens",
            "stop_sequence": "stop_sequence",
        }
        stop_reason = stop_reason_map.get(response.stop_reason or "end_turn", "end_turn")

        return {
            "text": "".join(text_parts),
            "thinking": "".join(thinking_parts),  # exposes chain-of-thought if caller wants it
            "raw_content": raw_content,           # verbatim blocks for replay across tool use
            "tool_calls": tool_calls,
            "stop_reason": stop_reason,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "raw": response,
        }
