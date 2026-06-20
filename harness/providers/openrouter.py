"""
OpenRouter provider (multi-model, OpenAI-compatible).

Uses the openai SDK pointed at https://openrouter.ai/api/v1.
Supports both tool-calling models (native) and plain-text models (tags mode).

"OpenClaw" is the user-facing nickname for this provider.
"""

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from harness.providers.base import BaseProvider, Message, ToolDefinition

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterProvider(BaseProvider):
    """
    Provider for any model available on OpenRouter.

    OpenRouter uses the OpenAI-compatible API format, making it trivial
    to swap models. The `model` argument to `complete()` should be the
    full OpenRouter model string, e.g. "openai/gpt-4o" or
    "meta-llama/llama-3.3-70b-instruct".

    When `tools` is None or empty, no tool definitions are sent
    (suitable for tags mode or plain-text models).
    """

    def __init__(
        self,
        api_key: str,
        app_name: str = "AgentHarness",
        app_url: str = "https://github.com/agent-harness",
    ) -> None:
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": app_url,
                "X-Title": app_name,
            },
        )

    def _convert_messages(self, messages: list[Message], system: str) -> list[dict[str, Any]]:
        """Convert our Message objects to OpenAI chat format."""
        result: list[dict[str, Any]] = []

        if system:
            result.append({"role": "system", "content": system})

        for msg in messages:
            if msg.role == "tool":
                # OpenAI tool results
                result.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id or "",
                    "content": msg.content,
                })
            elif msg.role == "assistant" and msg.tool_calls:
                # Assistant message with tool calls
                api_msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": msg.content or None,
                    "tool_calls": [
                        {
                            "id": tc.get("id", f"call_{i}"),
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": json.dumps(tc["arguments"])
                                if isinstance(tc["arguments"], dict)
                                else tc["arguments"],
                            },
                        }
                        for i, tc in enumerate(msg.tool_calls)
                    ],
                }
                result.append(api_msg)
            else:
                result.append({"role": msg.role, "content": msg.content})

        return result

    def _convert_tools(self, tools: list[ToolDefinition]) -> list[dict[str, Any]]:
        """Convert ToolDefinition objects to OpenAI function format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
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
    ) -> dict[str, Any]:
        """Run inference via OpenRouter API and return normalized response."""
        api_messages = self._convert_messages(messages, system)
        api_tools = self._convert_tools(tools) if tools else []

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if api_tools:
            kwargs["tools"] = api_tools
            kwargs["tool_choice"] = "auto"

        logger.debug(
            "OpenRouter request: model=%s, messages=%d, tools=%d",
            model, len(api_messages), len(api_tools)
        )

        response = await self.client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        msg = choice.message

        # Extract text content
        text = msg.content or ""

        # Extract tool calls
        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, AttributeError):
                    args = {"raw": tc.function.arguments if hasattr(tc, "function") else ""}
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": args,
                })

        # Map finish_reason to our internal stop_reason names
        finish_reason = choice.finish_reason or "stop"
        stop_reason_map = {
            "stop": "end_turn",
            "tool_calls": "tool_use",
            "length": "max_tokens",
            "content_filter": "stop_sequence",
        }
        stop_reason = stop_reason_map.get(finish_reason, "end_turn")

        usage = response.usage
        return {
            "text": text,
            "tool_calls": tool_calls,
            "stop_reason": stop_reason,
            "usage": {
                "input_tokens": usage.prompt_tokens if usage else 0,
                "output_tokens": usage.completion_tokens if usage else 0,
            },
            "raw": response,
        }
