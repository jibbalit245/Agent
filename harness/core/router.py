"""
Intelligent request router.

Analyzes incoming messages to determine:
  1. Task type (research, code, analysis, general, creative)
  2. Complexity (low, medium, high)
  3. Which model/provider to use
  4. Whether to chain specialized sub-agents

The router itself uses a cheap fast model to make these decisions,
so routing overhead is minimal.
"""

import logging
import json
from dataclasses import dataclass
from typing import Literal

from harness.providers.base import BaseProvider, Message

logger = logging.getLogger(__name__)

TaskType = Literal["research", "code", "analysis", "creative", "general"]
Complexity = Literal["low", "medium", "high"]


@dataclass
class RoutingDecision:
    task_type: TaskType
    complexity: Complexity
    model: str
    reasoning: str
    suggested_tools: list[str]


# Heuristic keywords for fast local classification (fallback if LLM routing fails)
_TASK_KEYWORDS: dict[TaskType, list[str]] = {
    "research": [
        "find", "search", "look up", "what is", "who is", "when did", "where is",
        "latest", "recent", "news", "article", "paper", "study", "research",
        "fact", "information about", "tell me about", "explain",
    ],
    "code": [
        "code", "script", "function", "class", "implement", "program", "python",
        "javascript", "debug", "error", "exception", "refactor", "write a",
        "create a function", "build a", "fix this", "syntax", "algorithm",
    ],
    "analysis": [
        "analyze", "compare", "evaluate", "assess", "review", "summarize",
        "pros and cons", "advantages", "disadvantages", "breakdown",
        "what do you think", "opinion", "critique",
    ],
    "creative": [
        "write a story", "poem", "creative", "imagine", "brainstorm",
        "ideas for", "suggest", "invent", "design",
    ],
}

_COMPLEXITY_SIGNALS: dict[Complexity, list[str]] = {
    "high": [
        "comprehensive", "detailed", "thorough", "deep dive", "in depth",
        "compare multiple", "analyze and", "step by step", "complete",
        "full implementation", "production", "architecture",
    ],
    "low": [
        "quick", "briefly", "simple", "short", "tldr", "summary", "just",
        "one line", "fast", "what's", "what is", "who is",
    ],
}


def _heuristic_classify(text: str) -> tuple[TaskType, Complexity]:
    """Fast local classification using keyword matching. O(n) with small constants."""
    text_lower = text.lower()

    # Task type
    task_scores: dict[str, int] = {t: 0 for t in _TASK_KEYWORDS}
    for task_type, keywords in _TASK_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                task_scores[task_type] += 1

    task_type: TaskType = max(task_scores, key=lambda k: task_scores[k])  # type: ignore
    if task_scores[task_type] == 0:
        task_type = "general"

    # Complexity
    complexity: Complexity = "medium"
    high_count = sum(1 for kw in _COMPLEXITY_SIGNALS["high"] if kw in text_lower)
    low_count = sum(1 for kw in _COMPLEXITY_SIGNALS["low"] if kw in text_lower)
    word_count = len(text.split())
    if word_count > 80 or high_count > 1:
        complexity = "high"
    elif word_count < 15 or low_count > 0:
        complexity = "low"

    return task_type, complexity


_ROUTER_SYSTEM = """You are a routing assistant. Analyze the user's request and return JSON.

Return ONLY valid JSON with these fields:
{
  "task_type": "research" | "code" | "analysis" | "creative" | "general",
  "complexity": "low" | "medium" | "high",
  "reasoning": "<one sentence>",
  "suggested_tools": ["web_search", "web_fetch", "python_exec", "memory_save", "memory_load", "spawn_agent", "summarize"]
}

task_type definitions:
- research: finding facts, current events, looking things up
- code: writing, debugging, or explaining code
- analysis: evaluating, comparing, summarizing, or critiquing content
- creative: stories, poems, brainstorming, open-ended generation
- general: conversation, simple questions, chit-chat

complexity definitions:
- low: simple one-step task, can be done in a single response
- medium: requires some tool use or multiple steps
- high: complex multi-step task, may need sub-agents

suggested_tools: which tools are likely needed (empty array if none)
"""


class Router:
    """
    Routes requests to the right model and suggests tools.

    Uses a fast LLM for routing decisions with fallback to keyword heuristics.
    """

    def __init__(
        self,
        provider: BaseProvider,
        router_model: str,
        brain_model: str,
        fast_model: str,
    ) -> None:
        self.provider = provider
        self.router_model = router_model
        self.brain_model = brain_model
        self.fast_model = fast_model

    async def route(self, user_message: str, conversation_history: list[Message]) -> RoutingDecision:
        """
        Analyze the user message and return a routing decision.

        First tries an LLM-based classification; falls back to heuristics on error.
        """
        try:
            return await self._llm_route(user_message)
        except Exception as exc:
            logger.warning("LLM routing failed (%s), falling back to heuristics", exc)
            return self._heuristic_route(user_message)

    async def _llm_route(self, user_message: str) -> RoutingDecision:
        """Use the router model to classify the request."""
        messages = [Message(role="user", content=f"Request to classify:\n\n{user_message}")]
        raw = await self.provider.complete(
            model=self.router_model,
            messages=messages,
            system=_ROUTER_SYSTEM,
            tools=None,
            temperature=0.0,
            max_tokens=256,
        )
        text = raw.get("text", "")
        # Strip markdown code fences if present
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        data = json.loads(text)
        task_type: TaskType = data.get("task_type", "general")
        complexity: Complexity = data.get("complexity", "medium")

        # Pick model based on complexity
        model = self._pick_model(complexity)

        return RoutingDecision(
            task_type=task_type,
            complexity=complexity,
            model=model,
            reasoning=data.get("reasoning", ""),
            suggested_tools=data.get("suggested_tools", []),
        )

    def _heuristic_route(self, user_message: str) -> RoutingDecision:
        """Keyword-based fallback routing."""
        task_type, complexity = _heuristic_classify(user_message)
        model = self._pick_model(complexity)

        # Suggest tools based on task type
        tool_map: dict[str, list[str]] = {
            "research": ["web_search", "web_fetch", "summarize"],
            "code": ["python_exec"],
            "analysis": ["summarize"],
            "creative": [],
            "general": [],
        }

        return RoutingDecision(
            task_type=task_type,
            complexity=complexity,
            model=model,
            reasoning="heuristic classification",
            suggested_tools=tool_map.get(task_type, []),
        )

    def _pick_model(self, complexity: Complexity) -> str:
        """Select model based on task complexity."""
        if complexity == "low":
            return self.fast_model
        elif complexity == "high":
            return self.brain_model
        else:
            return self.brain_model  # Default to brain for medium too
