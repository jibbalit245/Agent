"""
summarize tool — condense long text using a fast model.

This is injected at startup with a reference to the provider so it can
call the API. The provider is set via `set_provider()` before any calls.
"""

import logging
from typing import Any

from harness.tools.registry import registry

logger = logging.getLogger(__name__)

_provider: Any = None
_fast_model: str = "claude-haiku-4-5-20251001"

_MAX_INPUT_CHARS = 40000
_MAX_OUTPUT_TOKENS = 512

_SUMMARIZE_SYSTEM = (
    "You are a concise summarizer. Given text, produce a clear, accurate summary "
    "that captures the key points. Be brief but complete. Do not add commentary."
)


def set_provider(provider: Any, fast_model: str) -> None:
    """Configure the provider used for summarization. Called at startup."""
    global _provider, _fast_model
    _provider = provider
    _fast_model = fast_model
    logger.debug("summarize tool configured: model=%s", fast_model)


@registry.register(
    name="summarize",
    description=(
        "Condense long text into a concise summary. "
        "Useful for processing long web pages, documents, or tool outputs "
        "before including them in your response."
    ),
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text to summarize",
            },
            "max_words": {
                "type": "integer",
                "description": "Approximate maximum words in the summary (default 150)",
                "default": 150,
            },
        },
        "required": ["text"],
    },
)
async def summarize(text: str, max_words: int = 150) -> str:
    """Summarize text using a fast model."""
    if _provider is None:
        # Fallback: simple truncation
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words]) + " [...]"

    # Truncate very long inputs
    if len(text) > _MAX_INPUT_CHARS:
        text = text[:_MAX_INPUT_CHARS] + "\n[...text truncated for summarization]"

    from harness.providers.base import Message
    messages = [
        Message(
            role="user",
            content=f"Please summarize the following text in approximately {max_words} words:\n\n{text}",
        )
    ]

    try:
        result = await _provider.complete(
            model=_fast_model,
            messages=messages,
            system=_SUMMARIZE_SYSTEM,
            tools=None,
            temperature=0.3,
            max_tokens=_MAX_OUTPUT_TOKENS,
        )
        return result.get("text", "Summary unavailable.")
    except Exception as exc:
        logger.error("summarize failed: %s", exc)
        # Fallback truncation
        words = text.split()
        return " ".join(words[:max_words]) + " [...]"
