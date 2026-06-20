"""
council_consult — query Claude + GPT-4o in parallel, return both perspectives.

The calling agent (usually Claude) naturally synthesizes the two views.
This gives every agent access to cross-model reasoning without the user
having to orchestrate it manually.

Setup: call set_council_providers(providers, primary_model) in main.py
after providers are initialized.
"""

import asyncio
import logging
from typing import Any

from harness.providers.base import Message
from harness.tools.registry import registry

logger = logging.getLogger(__name__)

_providers: dict = {}
_primary_model: str = "claude-sonnet-4-6"
_fast_model: str = "claude-haiku-4-5-20251001"


def set_council_providers(
    providers: dict,
    primary_model: str = "claude-sonnet-4-6",
    fast_model: str = "claude-haiku-4-5-20251001",
) -> None:
    """Called once at startup to wire in the available providers."""
    global _providers, _primary_model, _fast_model
    _providers = providers
    _primary_model = primary_model
    _fast_model = fast_model


async def _query(provider: Any, model: str, system: str, content: str, max_tokens: int = 4096) -> str:
    try:
        result = await provider.complete(
            model=model,
            messages=[Message(role="user", content=content)],
            system=system,
            temperature=0.3,
            max_tokens=max_tokens,
        )
        return result.get("text", "").strip() or "(no response)"
    except Exception as exc:
        logger.warning("Council query failed for model %s: %s", model, exc)
        return f"[Error querying {model}: {exc}]"


@registry.register(
    name="council_consult",
    description=(
        "Get a second opinion by consulting multiple frontier AI models (Claude + GPT-4o) "
        "in parallel. Use this for high-stakes decisions, complex technical problems, "
        "mathematical proofs, scientific claims, architecture trade-offs, business strategy, "
        "or any question where independent verification adds confidence. Returns both "
        "perspectives so you can synthesize the best answer."
    ),
    parameters={
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The specific question or problem to put to the council.",
            },
            "context": {
                "type": "string",
                "description": "Background context the council members need to answer well.",
            },
            "depth": {
                "type": "string",
                "enum": ["fast", "thorough"],
                "description": (
                    "'fast' uses smaller models for quick takes. "
                    "'thorough' uses frontier models for deep analysis. Default: thorough."
                ),
            },
        },
        "required": ["question"],
    },
)
async def council_consult(
    question: str,
    context: str = "",
    depth: str = "thorough",
    **kwargs,
) -> str:
    if not _providers:
        return "Council unavailable: no providers configured."

    system = (
        "You are a world-class expert consultant. Give a direct, precise answer. "
        "Show your reasoning. State any assumptions or caveats explicitly. "
        "Be specific — avoid vague generalities. No filler, no hedging without substance."
    )

    content = question
    if context:
        content = f"Context:\n{context}\n\nQuestion:\n{question}"

    # Determine which models to use
    if depth == "fast":
        claude_model = _fast_model
        gpt_model = "openai/gpt-4o-mini"
        gpt_model_direct = "gpt-4o-mini"
    else:
        claude_model = _primary_model
        gpt_model = "openai/gpt-4o"
        gpt_model_direct = "gpt-4o"

    max_tokens = 2048 if depth == "fast" else 4096

    # Build parallel tasks
    tasks: dict[str, Any] = {}

    if "anthropic" in _providers:
        tasks["Claude"] = _query(_providers["anthropic"], claude_model, system, content, max_tokens)

    # GPT via direct OpenAI if available, else via OpenRouter
    if "openai" in _providers:
        tasks["GPT-4o"] = _query(_providers["openai"], gpt_model_direct, system, content, max_tokens)
    elif "openrouter" in _providers:
        tasks["GPT-4o"] = _query(_providers["openrouter"], gpt_model, system, content, max_tokens)

    if not tasks:
        return "Council unavailable: need anthropic and/or openrouter/openai providers."

    if len(tasks) == 1:
        # Only one model available — do a self-critique loop instead
        name, coro = next(iter(tasks.items()))
        first_answer = await coro
        critique_content = (
            f"Original question: {question}\n\n"
            f"Your initial answer:\n{first_answer}\n\n"
            "Now critique this answer: What did you get right? What might be wrong or incomplete? "
            "What would a skeptical expert challenge? Give a revised, stronger answer."
        )
        revised = await _query(
            next(iter(_providers.values())), claude_model, system, critique_content, max_tokens
        )
        return (
            f"## Initial Analysis\n{first_answer}\n\n"
            f"---\n\n"
            f"## Self-Critique & Revision\n{revised}"
        )

    # Run both in parallel
    results_list = await asyncio.gather(*tasks.values(), return_exceptions=True)
    results = {}
    for name, result in zip(tasks.keys(), results_list):
        if isinstance(result, Exception):
            results[name] = f"[Error: {result}]"
        else:
            results[name] = result

    # Format as clear dual-perspective output
    sections = []
    for name, text in results.items():
        sections.append(f"## {name}\n{text}")

    output = "\n\n---\n\n".join(sections)

    # Add convergence note if both answered
    if len(results) == 2:
        output += (
            "\n\n---\n\n"
            "*Council complete. Synthesize the above: where they agree = high confidence. "
            "Where they differ = warrants careful judgment.*"
        )

    return output
