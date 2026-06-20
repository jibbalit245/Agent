"""
HuggingFace Inference Router provider (OpenAI-compatible).

Uses the HuggingFace inference router at https://router.huggingface.co/v1,
authenticated via HF_TOKEN. This endpoint is OpenAI API-compatible.

Most models routed through HuggingFace (e.g. DeepSeek-R1-Distill variants)
do NOT support native tool calling, so `brain_mode="tags"` (XML tag
pass-through) is the recommended default for this provider. Tool definitions
passed to `complete()` are ignored — the caller is responsible for injecting
XML tool descriptions into the system prompt and parsing `<tool>` tags from
the response.
"""

import json
import logging
import os
from typing import Any

from openai import AsyncOpenAI

from harness.providers.base import BaseProvider, Message, ToolDefinition

logger = logging.getLogger(__name__)

HUGGINGFACE_BASE_URL = "https://router.huggingface.co/v1"

DEFAULT_MODEL = "huihui-ai/DeepSeek-R1-Distill-Qwen-32B-abliterated:featherless-ai"


class HuggingFaceProvider(BaseProvider):
    """
    Provider for models available via the HuggingFace Inference Router.

    The HuggingFace router exposes an OpenAI-compatible API, so we use the
    openai SDK pointed at a different base URL. Authentication is done via
    HF_TOKEN (passed as the Bearer token).

    Most models on this router (DeepSeek-R1-Distill, Qwen, Mistral fine-tunes,
    etc.) do not support API-level function calling. Use brain_mode="tags" so
    the orchestrator injects XML tool descriptions into the system prompt and
    parses tool invocations from the model's text output.

    When `tools` is provided (and the model actually supports it), tool
    definitions are forwarded using the OpenAI function-calling format.
    In practice, set brain_mode="tags" for this provider and leave `tools`
    empty.
    """

    def __init__(
        self,
        api_key: str | None = None,
    ) -> None:
        resolved_key = api_key or os.environ.get("HF_TOKEN", "")
        self.client = AsyncOpenAI(
            api_key=resolved_key,
            base_url=HUGGINGFACE_BASE_URL,
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
        """Run inference via HuggingFace Inference Router and return normalized response."""
        api_messages = self._convert_messages(messages, system)
        api_tools = self._convert_tools(tools) if tools else []

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
        if api_tools:
            kwargs["tools"] = api_tools
            kwargs["tool_choice"] = "auto"

        logger.debug(
            "HuggingFace request: model=%s, messages=%d, tools=%d",
            model, len(api_messages), len(api_tools),
        )

        response = await self.client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        msg = choice.message

        # Extract text content
        text = msg.content or ""

        # Extract tool calls (only relevant for models that support native tool calling)
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
