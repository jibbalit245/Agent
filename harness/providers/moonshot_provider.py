"""
Moonshot AI (Kimi) provider.

Moonshot exposes an OpenAI-compatible API, so we use the openai SDK pointed
at the Moonshot base URL. Kimi K2 offers a large context window (~256K tokens),
native tool/function calling, and strong reasoning — it serves as both a
council member and the long-context engine in this harness.

Models:
  kimi-k2-0711-preview   — flagship, ~256K context, tool use
  kimi-latest            — latest general model
  moonshot-v1-128k       — 128K context
  moonshot-v1-32k        — 32K context
  moonshot-v1-8k         — 8K context
"""

import json
import logging
from typing import Any

import openai

from harness.providers.base import BaseProvider, Message, ToolDefinition

logger = logging.getLogger(__name__)

_MOONSHOT_BASE_URL = "https://api.moonshot.ai/v1"


class MoonshotProvider(BaseProvider):
    """Provider for Moonshot AI (Kimi) models via their OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = _MOONSHOT_BASE_URL,
    ) -> None:
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def _convert_messages(self, messages: list[Message], system: str) -> list[dict[str, Any]]:
        """Convert our Message objects to OpenAI chat format."""
        result: list[dict[str, Any]] = []

        if system:
            result.append({"role": "system", "content": system})

        for msg in messages:
            if msg.role == "tool":
                result.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id or "",
                    "content": msg.content,
                })
            elif msg.role == "assistant" and msg.tool_calls:
                tool_calls_data = [
                    {
                        "id": tc.get("id", f"call_{i}"),
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": (
                                json.dumps(tc["arguments"])
                                if isinstance(tc["arguments"], dict)
                                else tc["arguments"]
                            ),
                        },
                    }
                    for i, tc in enumerate(msg.tool_calls)
                ]
                result.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": tool_calls_data,
                })
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
        thinking: dict | None = None,
        extra_body: dict | None = None,
    ) -> dict[str, Any]:
        """
        Run inference via Moonshot and return a normalized response.

        `extra_body` is passed straight through to the OpenAI SDK, which injects
        it into the request JSON. This is how Kimi-specific features are enabled:
          - Agent Swarm:   {"swarm": {"max_agents": N}}   (N in 1..300)
          - Instant mode:  {"chat_template_kwargs": {"thinking": False}}
        """
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
        if extra_body:
            kwargs["extra_body"] = extra_body

        logger.debug(
            "Moonshot request: model=%s, messages=%d, tools=%d, extra_body=%s",
            model, len(api_messages), len(api_tools), bool(extra_body),
        )

        response = await self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        msg = choice.message

        text = msg.content or ""
        tool_calls = []

        if msg.tool_calls:
            for tc in msg.tool_calls:
                args = tc.function.arguments
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {"raw": args}
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": args,
                })

        finish_reason_map = {
            "stop": "end_turn",
            "tool_calls": "tool_use",
            "length": "max_tokens",
            "content_filter": "stop_sequence",
        }
        stop_reason = finish_reason_map.get(choice.finish_reason or "stop", "end_turn")
        if tool_calls:
            stop_reason = "tool_use"

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
