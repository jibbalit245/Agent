"""
swarm_solve — dispatch a task to Kimi K2.6's native server-side Agent Swarm.

Kimi K2.6 decomposes a task across up to 300 domain-specialized sub-agents
(up to 4,000 coordinated steps), routes the work, and synthesizes the result
server-side. The harness just hands it the task and a max_agents budget and
gets back the finished answer — no client-side orchestration required.

Invoked via the OpenAI-compatible API with:
    extra_body = {"swarm": {"max_agents": N}}   # N in 1..300

Setup: call set_swarm_provider(provider, model) in main.py after the Moonshot
provider is initialized. If Moonshot isn't configured, the tool returns a
graceful error.
"""

import logging
from typing import Any

from harness.providers.base import Message
from harness.tools.registry import registry

logger = logging.getLogger(__name__)

_provider: Any = None
_model: str = "kimi-k2.6"
_default_max_agents: int = 50
_AGENT_CAP = 300  # Kimi K2.6 hard limit


def set_swarm_provider(provider: Any, model: str, default_max_agents: int = 50) -> None:
    """Called once at startup to wire in the swarm provider and model."""
    global _provider, _model, _default_max_agents
    _provider = provider
    _model = model
    _default_max_agents = max(1, min(default_max_agents, _AGENT_CAP))
    logger.info("Swarm provider set: model=%s, default_max_agents=%d", model, _default_max_agents)


@registry.register(
    name="swarm_solve",
    description=(
        "Dispatch a large, multi-part, or research-heavy task to Kimi K2.6's native "
        "Agent Swarm. Kimi decomposes the task across many specialized sub-agents "
        "(up to 300), runs them in parallel server-side, and returns one synthesized "
        "result. Use this for jobs that genuinely benefit from parallel decomposition: "
        "broad research sweeps, large refactors, multi-document analysis, build-out tasks "
        "with many independent parts. For a single focused question, answer directly or "
        "use council_consult instead — the swarm shines on breadth, not on one hard step.\n\n"
        "CRITICAL: the swarm is garbage-sensitive. A vague `task` makes it spawn "
        "overlapping, conflicting sub-agents and the output is mush. ALWAYS pass a "
        "STRUCTURED BRIEF as `task`, containing: (1) one clear Objective; (2) the exact "
        "Final Deliverable format; (3) Shared Context all sub-agents need; (4) explicitly "
        "named, independent Parallelizable Work Units, each with scope/input/output; "
        "(5) how the units integrate; (6) constraints & success criteria. Set `max_agents` "
        "to roughly the number of independent work units. If you can't name the independent "
        "units, the task isn't swarm-shaped — don't use this tool."
    ),
    parameters={
        "type": "object",
        "properties": {
            "task": {
                "type": "string",
                "description": (
                    "The full task to hand to the swarm. Be specific and complete — "
                    "the swarm decomposes this into sub-tasks itself, so give it the "
                    "whole objective, constraints, and any required output format."
                ),
            },
            "context": {
                "type": "string",
                "description": "Background, source material, or constraints the swarm needs.",
            },
            "max_agents": {
                "type": "integer",
                "description": (
                    "Maximum sub-agents to spawn (1-300). More agents = broader parallelism "
                    "for bigger tasks, but higher cost/latency. Default 50. Use 10-30 for "
                    "moderate tasks, 100+ only for genuinely large decomposable work."
                ),
            },
        },
        "required": ["task"],
    },
)
async def swarm_solve(
    task: str,
    context: str = "",
    max_agents: int = 0,
    **kwargs,
) -> str:
    if _provider is None:
        return (
            "swarm_solve unavailable: no Moonshot provider configured. "
            "Set MOONSHOT_API_KEY and restart."
        )

    n_agents = max_agents if max_agents > 0 else _default_max_agents
    n_agents = max(1, min(int(n_agents), _AGENT_CAP))

    system = (
        "You are the lead of an agent swarm. Decompose the task, delegate across your "
        "sub-agents, and synthesize their work into one complete, coherent result. "
        "Deliver the finished output — not a plan of what you would do."
    )

    user_message = task if not context else f"CONTEXT:\n{context}\n\n---\n\nTASK:\n{task}"

    try:
        result = await _provider.complete(
            model=_model,
            messages=[Message(role="user", content=user_message)],
            system=system,
            temperature=1.0,  # K2.6 recommends 1.0 for thinking/agentic mode
            max_tokens=8192,
            extra_body={"swarm": {"max_agents": n_agents}},
        )
        text = result.get("text", "").strip()
        usage = result.get("usage", {})
        footer = ""
        if usage:
            footer = (
                f"\n\n---\n_Swarm: up to {n_agents} sub-agents | "
                f"{usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out tokens_"
            )
        return (text or "(swarm returned an empty response)") + footer
    except Exception as exc:
        logger.error("swarm_solve failed: %s", exc)
        return f"[swarm_solve error: {type(exc).__name__}: {exc}]"
