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


# System prompt designed to feel like a knowledgeable colleague
_DEFAULT_SYSTEM = """You are a knowledgeable, resourceful AI assistant with access to powerful tools.

You feel like a smart colleague: curious, direct, and genuinely helpful. You proactively use tools
when needed — you don't wait to be asked. If something would benefit from a web search, you search.
If code needs to run to verify, you run it. If the user might want to know something adjacent, you
find it.

Guidelines:
- Use tools proactively without mentioning that you're doing so
- Synthesize tool results naturally into your response — don't dump raw output
- Be concise but complete; skip unnecessary preamble
- If you make assumptions, state them briefly
- For multi-step tasks, plan first, then execute
- When uncertain about current facts, search rather than guessing
- Cite sources when you fetch specific information from the web

You have access to the following capabilities (use them freely):
- web_search: Search the web for current information
- web_fetch: Retrieve and read the content of any URL
- python_exec: Run Python code to compute, analyze, or generate
- memory_save / memory_load: Persist information across conversations
- spawn_agent: Create a specialized sub-agent to handle a specific sub-task
- summarize: Condense long text using a fast model

Never tell the user you "can't" do something without first trying the available tools.
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
