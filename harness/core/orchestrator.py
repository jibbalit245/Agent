"""
Main agentic loop orchestrator.

Drives the Brain through repeated tool-use cycles until:
  - The model stops requesting tools (stop_reason == "end_turn")
  - Max iterations is reached
  - An unrecoverable error occurs

Supports both native (API tool calling) and tags (XML pass-through) modes.
"""

import logging
from dataclasses import dataclass
from typing import Any

from harness.core.brain import Brain
from harness.core.tag_parser import inject_tool_result, strip_tool_tags, has_tool_calls
from harness.providers.base import Message, ToolDefinition
from harness.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorResult:
    """Final result returned from a completed orchestration run."""
    text: str
    iterations: int
    tool_calls_made: list[dict[str, Any]]
    stopped_reason: str  # "end_turn" | "max_iterations" | "error"


_DEFAULT_SYSTEM = """You are a sharp, capable AI assistant. You reason carefully, pursue intent over \
literal words, and get things done without hand-holding.

## How you think

**Intent over literalism.** Always ask: what is this person actually trying to achieve? Follow that \
goal — not technicalities in how they phrased it. If someone says "don't let anyone in after 10pm," \
they mean through any entry point. Never exploit loopholes. If you're unsure what they want, ask one \
targeted question — don't guess wrong.

**Think before acting.** For anything non-trivial, reason through the problem before executing. \
Consider edge cases, failure modes, and whether your plan actually achieves the goal.

**Complete tasks fully.** Do the whole job. Not the easy 80% — all of it. If you hit a blocker, \
say exactly what it is and what you've already tried. Don't silently skip hard parts.

**Own your mistakes.** If you got something wrong, say so directly and fix it. No rationalizing.

## How you use tools

Use tools aggressively — they exist to make your answers accurate and complete:

- **knowledge_search** — check this FIRST for any platform-specific question (setup, APIs, pricing, \
model names, env vars). It has curated docs for Anthropic, HuggingFace, OpenRouter, OpenAI, AWS, \
Google Cloud, RunPod, Replit, GitHub, and more.
- **web_search** — use when you need current info or the knowledge base doesn't cover it
- **web_fetch** — read the full page when a search snippet isn't enough
- **python_exec** — run code to compute, verify, or analyze instead of estimating
- **memory_save / memory_load** — remember things the user tells you across conversations; \
proactively load memory at the start of relevant conversations
- **summarize** — condense long content before including it in your response

You do NOT need permission to use tools. Don't announce you're using them — just use them and \
synthesize the results naturally. Never claim you can't do something without actually trying.

## How you communicate

- Skip preamble. Answer first, explain after if needed.
- Be direct. No "certainly!", "great question!", or throat-clearing.
- Show, don't tell: run the code and show output rather than describing what you'd do.
- Cite sources when you retrieve specific facts from the web.
- When a task is done, state what you did — not what you plan to do.
"""


class Orchestrator:
    """
    Runs the full agentic loop for a single user turn.

    Flow:
      1. Call brain.complete() with current conversation + tools
      2. If tool_calls in response → execute each via tool registry
      3. Append tool results to conversation
      4. Repeat until no tool calls or max_iterations reached
      5. Return final text response
    """

    def __init__(
        self,
        brain: Brain,
        tool_registry: ToolRegistry,
        max_iterations: int = 10,
        system_prompt: str = _DEFAULT_SYSTEM,
        enabled_tools: list[str] | None = None,
    ) -> None:
        self.brain = brain
        self.tool_registry = tool_registry
        self.max_iterations = max_iterations
        self.system_prompt = system_prompt
        # None means all tools; a list restricts to that subset
        self.enabled_tools: list[str] | None = enabled_tools
        # Inject system into brain
        self.brain.system_prompt = system_prompt

    async def run(
        self,
        user_message: str,
        history: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> OrchestratorResult:
        """
        Execute the full agentic loop for a single user turn.

        `history` should contain the conversation so far (not including the
        current user_message). It will NOT be mutated.
        """
        # Build working message list for this turn
        messages: list[Message] = list(history) + [Message(role="user", content=user_message)]
        tools: list[ToolDefinition] = self.tool_registry.get_definitions(subset=self.enabled_tools)

        iteration = 0
        all_tool_calls: list[dict[str, Any]] = []
        final_text = ""
        stopped_reason = "end_turn"

        while iteration < self.max_iterations:
            iteration += 1
            logger.debug("Orchestrator iteration %d/%d", iteration, self.max_iterations)

            response = await self.brain.complete(
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            stop_reason = response.get("stop_reason", "end_turn")
            tool_calls: list[dict[str, Any]] = response.get("tool_calls", [])
            text: str = response.get("text", "")

            logger.debug("Stop reason: %s | Tool calls: %d", stop_reason, len(tool_calls))

            if not tool_calls:
                # No tools requested — done
                final_text = text
                stopped_reason = "end_turn"
                break

            # Execute all tool calls in this response
            if self.brain.mode == "native":
                # In native mode: append assistant message with tool_calls, then tool results
                messages.append(Message(
                    role="assistant",
                    content=text,
                    tool_calls=[
                        {"id": tc.get("id", f"call_{i}"), "name": tc["name"], "arguments": tc["arguments"]}
                        for i, tc in enumerate(tool_calls)
                    ],
                ))

                for tc in tool_calls:
                    result = await self._execute_tool(tc["name"], tc["arguments"])
                    all_tool_calls.append({
                        "name": tc["name"],
                        "arguments": tc["arguments"],
                        "result": result,
                    })
                    tool_id = tc.get("id", f"call_{iteration}")
                    messages.append(Message(
                        role="tool",
                        content=result,
                        tool_call_id=tool_id,
                        tool_name=tc["name"],
                    ))

            else:
                # Tags mode: inject results inline into the assistant text
                augmented_text = text
                for tc in tool_calls:
                    result = await self._execute_tool(tc["name"], tc["arguments"])
                    all_tool_calls.append({
                        "name": tc["name"],
                        "arguments": tc["arguments"],
                        "result": result,
                    })
                    from harness.core.tag_parser import ToolCall as TC, inject_tool_result
                    fake_call = TC(name=tc["name"], arguments=tc["arguments"], raw_tag=tc["_raw_tag"])
                    augmented_text = inject_tool_result(augmented_text, fake_call, result)

                # Append the augmented assistant message back to history
                messages.append(Message(role="assistant", content=augmented_text))

                # Ask the model to continue with a follow-up user turn
                messages.append(Message(
                    role="user",
                    content="Please continue based on the tool results above.",
                ))

            # If stop_reason was "end_turn" despite tool calls being present
            # (can happen in tags mode on final pass), break
            if stop_reason == "end_turn" and not tool_calls:
                final_text = text
                break

        else:
            # Loop exhausted
            logger.warning("Max iterations (%d) reached", self.max_iterations)
            final_text = text if text else "I reached the maximum number of tool-use steps. Here's what I found so far."
            stopped_reason = "max_iterations"

        # For tags mode, strip any remaining tool tags from the final output
        if self.brain.mode == "tags":
            final_text = strip_tool_tags(final_text)

        return OrchestratorResult(
            text=final_text.strip(),
            iterations=iteration,
            tool_calls_made=all_tool_calls,
            stopped_reason=stopped_reason,
        )

    async def _execute_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute a single tool call and return the string result."""
        logger.debug("Executing tool: %s(%s)", name, arguments)
        try:
            result = await self.tool_registry.dispatch(name, arguments)
            logger.debug("Tool %s result (%d chars)", name, len(str(result)))
            return str(result)
        except Exception as exc:
            error_msg = f"Tool '{name}' failed: {type(exc).__name__}: {exc}"
            logger.error(error_msg, exc_info=True)
            return error_msg
