"""
Direct OpenAI provider — wraps openai.AsyncOpenAI against api.openai.com.

Used by the council tool when OPENAI_API_KEY is set, giving direct GPT access
independent of OpenRouter. Supports reasoning_effort for o-series models.
"""

import logging
from typing import Any

from harness.providers.base import BaseProvider, Message, ToolDefinition

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """Direct OpenAI API provider (api.openai.com/v1)."""

    def __init__(self, api_key: str) -> None:
        try:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=api_key)
        except ImportError as exc:
            raise RuntimeError("openai package required: pip install openai") from exc

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
        formatted = []
        if system:
            formatted.append({"role": "system", "content": system})
        for m in messages:
            formatted.append({"role": m.role, "content": m.content})

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": formatted,
            "max_tokens": max_tokens,
        }

        is_reasoning = any(x in model.lower() for x in ("o1", "o3", "o4"))
        if not is_reasoning:
            kwargs["temperature"] = temperature

        if thinking and thinking.get("enabled") and is_reasoning:
            effort = thinking.get("effort", "high")
            kwargs["reasoning_effort"] = effort

        if tools:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    },
                }
                for t in tools
            ]
            kwargs["tool_choice"] = "auto"

        try:
            response = await self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            logger.error("OpenAI API error: %s", exc)
            raise

        msg = response.choices[0].message
        text = msg.content or ""

        tool_calls = []
        if msg.tool_calls:
            import json
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except Exception:
                    args = {}
                tool_calls.append({"name": tc.function.name, "arguments": args, "id": tc.id})

        return {
            "text": text,
            "tool_calls": tool_calls,
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
            },
        }
