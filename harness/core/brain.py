"""
Brain interface - unified layer over model providers.

Handles both modes:
  - native: Provider's built-in tool/function calling API
  - tags:   XML tag pass-through for non-tool-capable models

The Brain object is configured once at startup and reused across requests.
"""

import logging
from typing import Any

from harness.core.tag_parser import parse_tool_calls, inject_tool_result, has_tool_calls, strip_tool_tags
from harness.providers.base import BaseProvider, Message, ToolDefinition

logger = logging.getLogger(__name__)


class Brain:
    """
    Wraps a provider and executes one round of inference.

    For native mode: sends tool definitions to the API and handles
    structured tool_use responses.

    For tags mode: sends a system prompt instructing the model to emit
    XML tool tags, then parses those tags from the text response.
    """

    def __init__(
        self,
        provider: BaseProvider,
        model: str,
        mode: str = "native",
        system_prompt: str = "",
    ) -> None:
        if mode not in ("native", "tags"):
            raise ValueError(f"mode must be 'native' or 'tags', got {mode!r}")
        self.provider = provider
        self.model = model
        self.mode = mode
        self.system_prompt = system_prompt

    def _tags_system_addendum(self, tools: list[ToolDefinition]) -> str:
        """
        Build the XML tag instruction block appended to the system prompt
        when running in tags mode.
        """
        lines = [
            "",
            "## Tool Usage",
            "You have access to tools. To use a tool, output an XML block like this:",
            "",
            '    <tool name="TOOL_NAME">',
            "      <argument_name>value</argument_name>",
            "    </tool>",
            "",
            "After each tool call I will inject a <tool_result> block with the output.",
            "Keep calling tools until you have enough information to answer, then give",
            "your final answer without any more tool tags.",
            "",
            "Available tools:",
        ]
        for tool in tools:
            lines.append(f"\n### {tool.name}")
            lines.append(tool.description)
            if tool.parameters.get("properties"):
                lines.append("Parameters:")
                for param, schema in tool.parameters["properties"].items():
                    required = param in tool.parameters.get("required", [])
                    req_str = " (required)" if required else " (optional)"
                    desc = schema.get("description", "")
                    lines.append(f"  - {param}{req_str}: {desc}")
        return "\n".join(lines)

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
            "raw": Any,                   # raw provider response
          }
        """
        tools = tools or []

        if self.mode == "native":
            return await self._complete_native(messages, tools, temperature, max_tokens)
        else:
            return await self._complete_tags(messages, tools, temperature, max_tokens)

    async def _complete_native(
        self,
        messages: list[Message],
        tools: list[ToolDefinition],
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        system = self.system_prompt
        raw = await self.provider.complete(
            model=self.model,
            messages=messages,
            system=system,
            tools=tools if tools else None,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return raw

    async def _complete_tags(
        self,
        messages: list[Message],
        tools: list[ToolDefinition],
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        """
        Tags mode: augment system prompt with tool instructions, send as a
        plain-text completion, then parse XML tool tags from the response.
        """
        system = self.system_prompt
        if tools:
            system = system + self._tags_system_addendum(tools)

        raw = await self.provider.complete(
            model=self.model,
            messages=messages,
            system=system,
            tools=None,  # No native tools — we handle it ourselves
            temperature=temperature,
            max_tokens=max_tokens,
        )

        text: str = raw.get("text", "")

        # Convert XML tag calls into the same structure native mode returns
        parsed_calls = parse_tool_calls(text)
        tool_calls = [
            {"name": c.name, "arguments": c.arguments, "id": None, "_raw_tag": c.raw_tag}
            for c in parsed_calls
        ]

        stop_reason = "tool_use" if tool_calls else raw.get("stop_reason", "end_turn")

        return {
            "text": text,
            "tool_calls": tool_calls,
            "stop_reason": stop_reason,
            "raw": raw,
        }

    def build_tool_result_message(
        self,
        tool_name: str,
        tool_id: str | None,
        result: str,
        original_text: str = "",
    ) -> Message:
        """
        Build the message that carries tool results back to the model.

        - native mode: provider-specific tool_result format
        - tags mode:   inject result inline into the assistant text
        """
        if self.mode == "native":
            return Message(
                role="tool",
                content=result,
                tool_call_id=tool_id,
                tool_name=tool_name,
            )
        else:
            # For tags mode, we modify the assistant text in place.
            # The orchestrator passes `original_text` which already has tool tags;
            # we return it as an assistant message with results injected.
            # (The orchestrator handles multi-call accumulation.)
            return Message(
                role="assistant",
                content=original_text,
            )
