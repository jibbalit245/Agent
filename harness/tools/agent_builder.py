"""
Sub-agent spawning and text summarization tools.

spawn_agent: Creates a minimal agent with custom instructions and runs a task.
summarize: Uses a fast model to condense long text.
"""

import logging
from typing import Any, Callable, Awaitable

from harness.providers.base import BaseProvider, Message

logger = logging.getLogger(__name__)

_DEFAULT_SUB_AGENT_SYSTEM = """You are a specialized sub-agent. Complete the given task thoroughly
and return your result directly. Be concise but complete. Do not engage in conversation."""

_SUMMARIZE_SYSTEM = """You are a precise summarizer. Condense the provided text according to any
instructions given. Return only the summary — no preamble, no meta-commentary."""


def make_spawn_agent_handler(
    provider: BaseProvider,
    default_model: str,
) -> Callable[[dict[str, Any]], Awaitable[str]]:
    """
    Factory returning a spawn_agent handler bound to the given provider.

    The sub-agent runs without tools (it's a one-shot completion).
    For complex sub-tasks with tool use, the orchestrator should handle them
    directly or spawn a full Orchestrator instance.
    """

    async def spawn_agent(args: dict[str, Any]) -> str:
        task: str = args.get("task", "")
        system_prompt: str = args.get("system_prompt", _DEFAULT_SUB_AGENT_SYSTEM)
        model: str = args.get("model", default_model)

        if not task:
            return "Error: 'task' argument is required"

        logger.debug("spawn_agent: model=%s, task_len=%d", model, len(task))

        messages = [Message(role="user", content=task)]

        try:
            raw = await provider.complete(
                model=model,
                messages=messages,
                system=system_prompt,
                tools=None,
                temperature=0.5,
                max_tokens=2048,
            )
            result = raw.get("text", "")
            if not result:
                return "Sub-agent returned empty response"
            return f"Sub-agent result:\n{result}"
        except Exception as exc:
            logger.error("spawn_agent failed: %s", exc, exc_info=True)
            return f"Sub-agent failed: {type(exc).__name__}: {exc}"

    return spawn_agent


def make_summarize_handler(
    provider: BaseProvider,
    fast_model: str,
) -> Callable[[dict[str, Any]], Awaitable[str]]:
    """
    Factory returning a summarize handler using the given fast model.
    """

    async def summarize(args: dict[str, Any]) -> str:
        text: str = args.get("text", "")
        instruction: str = args.get("instruction", "")
        max_words: int = int(args.get("max_words", 150))

        if not text:
            return "Error: 'text' argument is required"

        prompt_parts = [f"Please summarize the following text in approximately {max_words} words."]
        if instruction:
            prompt_parts.append(f"Focus: {instruction}")
        prompt_parts.append(f"\n\nText to summarize:\n{text}")

        user_message = "\n".join(prompt_parts)
        messages = [Message(role="user", content=user_message)]

        logger.debug("summarize: model=%s, text_len=%d, max_words=%d", fast_model, len(text), max_words)

        try:
            raw = await provider.complete(
                model=fast_model,
                messages=messages,
                system=_SUMMARIZE_SYSTEM,
                tools=None,
                temperature=0.3,
                max_tokens=512,
            )
            summary = raw.get("text", "")
            if not summary:
                return "Summarization returned empty result"
            return summary
        except Exception as exc:
            logger.error("summarize failed: %s", exc, exc_info=True)
            return f"Summarization failed: {type(exc).__name__}: {exc}"

    return summarize
