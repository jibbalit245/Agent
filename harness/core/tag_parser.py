"""
XML tag parser for non-tool-capable models.

When BRAIN_MODE=tags, the brain outputs tool invocations as XML tags:
    <tool name="web_search"><query>latest news on X</query></tool>

This module finds those tags in model output, extracts the call details,
and produces formatted <tool_result> injections to feed back to the model.
"""

import re
import logging
from dataclasses import dataclass
from typing import Any
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """A single parsed tool call extracted from model output."""
    name: str
    arguments: dict[str, Any]
    raw_tag: str  # The original XML string, for replacement


def parse_tool_calls(text: str) -> list[ToolCall]:
    """
    Find all <tool name="...">...</tool> blocks in text.

    Returns a list of ToolCall objects in order of appearance.
    Malformed XML is skipped with a warning rather than raising.
    """
    calls: list[ToolCall] = []

    # Match <tool name="...">...</tool> blocks (non-greedy, allow newlines)
    pattern = re.compile(
        r'<tool\s+name=["\']([^"\']+)["\'][^>]*>(.*?)</tool>',
        re.DOTALL | re.IGNORECASE,
    )

    for match in pattern.finditer(text):
        tool_name = match.group(1).strip()
        inner_xml = match.group(2).strip()
        raw_tag = match.group(0)

        # Parse inner XML to extract arguments as a dict.
        # Each child element becomes a key-value pair.
        args: dict[str, Any] = {}
        try:
            # Wrap in a root element so ElementTree can parse it
            wrapped = f"<root>{inner_xml}</root>"
            root = ET.fromstring(wrapped)
            for child in root:
                # Text content or nested XML as string
                if len(child) == 0:
                    args[child.tag] = child.text or ""
                else:
                    # Nested XML → convert back to string
                    args[child.tag] = ET.tostring(child, encoding="unicode")
        except ET.ParseError as exc:
            logger.warning("Failed to parse tool call XML for %r: %s — using raw text", tool_name, exc)
            # Fall back: treat entire inner text as a single "input" argument
            args = {"input": inner_xml}

        calls.append(ToolCall(name=tool_name, arguments=args, raw_tag=raw_tag))
        logger.debug("Parsed tool call: %s(%s)", tool_name, args)

    return calls


def inject_tool_result(text: str, call: ToolCall, result: str) -> str:
    """
    Replace the tool call tag in `text` with the tool call + result block.

    The result is injected as:
        <tool name="...">...</tool>
        <tool_result name="...">
        [result]
        </tool_result>

    This keeps the model's output intact while appending the result inline.
    """
    replacement = (
        f"{call.raw_tag}\n"
        f"<tool_result name=\"{call.name}\">\n"
        f"{result}\n"
        f"</tool_result>"
    )
    # Replace only the first occurrence (in case of duplicate identical calls)
    return text.replace(call.raw_tag, replacement, 1)


def strip_tool_tags(text: str) -> str:
    """
    Remove all <tool ...> and <tool_result ...> blocks from text,
    returning only the human-readable parts of the model response.
    """
    # Remove tool call blocks
    text = re.sub(
        r'<tool\s+name=["\'][^"\']+["\'][^>]*>.*?</tool>',
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # Remove tool result blocks
    text = re.sub(
        r'<tool_result\s+name=["\'][^"\']+["\'][^>]*>.*?</tool_result>',
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return text.strip()


def has_tool_calls(text: str) -> bool:
    """Quick check: does the text contain any tool call tags?"""
    return bool(re.search(
        r'<tool\s+name=["\'][^"\']+["\']',
        text,
        re.IGNORECASE,
    ))
