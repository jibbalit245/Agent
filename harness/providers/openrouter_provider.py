"""
OpenRouter provider.

Proxies requests through OpenRouter's OpenAI-compatible API, allowing
access to hundreds of models (GPT-4, Gemini, Llama, Mistral, etc.)
from a single endpoint.

Uses the openai SDK since OpenRouter is fully OpenAI-compatible.
"""

import json
import logging
from typing import Any

import openai

from harness.providers.base import BaseProvider, Message, ToolDefinition

logger = logging.getLogger(__name__)

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterProvider(BaseProvider):
    """
    Provider for any model accessible via OpenRouter.

    Supports:
      - Native tool/function calling (OpenAI function format)
      - All models on OpenRouter that support tool use
    """

    def __init__(
        self,
        api_key: str,
        app_name: str = "AgentHarness",
        app_url: str = "https://github.com/agent-harness",
        base_url: str = _OPENROUTER_BASE_URL,
    ) -> None:
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": app_url,
                "X-Title": app_name,
            },
        )

    def _convert_messages(self, messages: list[Message], system: str) -> list[dict[str, Any]]:
        """Convert our Message objects to OpenAI API format."""
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
    ) -> dict[str, Any]:
        """Run inference via OpenRouter and return normalized response."""
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

        # reasoning_effort for OpenAI o-series and compatible models via OpenRouter
        if thinking and thinking.get("enabled"):
            effort = thinking.get("effort", "high")
            model_lower = model.lower()
            if any(x in model_lower for x in ("o1", "o3", "o4", "reasoning")):
                kwargs["reasoning_effort"] = effort
                kwargs.pop("temperature", None)  # o-series ignores temperature

        logger.debug(
            "OpenRouter request: model=%s, messages=%d, tools=%d",
            model, len(api_messages), len(api_tools),
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

        # Map finish_reason to our internal stop_reason names
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
