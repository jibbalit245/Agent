"""
long_context_read — route large content through Kimi K2's ~256K-token context window.

Use this when content is too large for standard models (whole codebases, large
document sets, long conversation logs, multi-file dumps). Kimi ingests the full
payload in a single pass; you get a targeted answer without chunking or summarizing.

Setup: call set_long_context_provider(provider, model) in main.py after providers
are initialized. If no provider is wired up, the tool returns a graceful error.
"""

import logging
from typing import Any

from harness.providers.base import Message
from harness.tools.registry import registry

logger = logging.getLogger(__name__)

_provider: Any = None
_model: str = "kimi-k2-0711-preview"


def set_long_context_provider(provider: Any, model: str) -> None:
    """Called once at startup to wire in the long-context provider and model."""
    global _provider, _model
    _provider = provider
    _model = model
    logger.info("Long-context provider set: model=%s", model)


@registry.register(
    name="long_context_read",
    description=(
        "Send a large body of text to Kimi K2 (~256K-token context window) and get a "
        "targeted answer. Use this when content is too big for standard models: entire "
        "codebases, large document collections, big log files, multi-file dumps. "
        "Kimi reads the full content in one shot — no chunking needed. "
        "Provide the raw content and a specific question or task."
    ),
    parameters={
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": (
                    "The large body of text to analyze. Can be code, documents, logs, "
                    "or any text content up to ~256K tokens — Kimi handles it."
                ),
            },
            "question": {
                "type": "string",
                "description": (
                    "What you want from the content: a specific question, an extraction task, "
                    "an analysis request, or a summarization instruction."
                ),
            },
            "format": {
                "type": "string",
                "enum": ["answer", "summary", "extract", "analyze"],
                "description": (
                    "'answer' — direct answer to a question (default). "
                    "'summary' — concise summary of the content. "
                    "'extract' — pull out specific data, patterns, or items. "
                    "'analyze' — deep structural or logical analysis."
                ),
            },
        },
        "required": ["content", "question"],
    },
)
async def long_context_read(
    content: str,
    question: str,
    format: str = "answer",
    **kwargs,
) -> str:
    if _provider is None:
        return (
            "long_context_read unavailable: no long-context provider configured. "
            "Set MOONSHOT_API_KEY and restart."
        )

    format_instructions = {
        "answer": "Answer the question directly and precisely. Cite the relevant section if applicable.",
        "summary": "Produce a concise, dense summary. Preserve all critical facts and figures.",
        "extract": "Extract exactly what is requested. Return structured output where possible.",
        "analyze": (
            "Perform a thorough structural and logical analysis. "
            "Identify patterns, anomalies, dependencies, and key insights."
        ),
    }

    system = (
        "You are a precise document analyst with access to the user's full content. "
        "Work only from what is provided — do not add external assumptions. "
        f"{format_instructions.get(format, format_instructions['answer'])}"
    )

    user_message = f"CONTENT:\n{content}\n\n---\n\nTASK:\n{question}"

    try:
        result = await _provider.complete(
            model=_model,
            messages=[Message(role="user", content=user_message)],
            system=system,
            temperature=0.2,
            max_tokens=8192,
        )
        text = result.get("text", "").strip()
        return text or "(Kimi returned an empty response)"
    except Exception as exc:
        logger.error("long_context_read failed: %s", exc)
        return f"[long_context_read error: {type(exc).__name__}: {exc}]"
