"""
Tool registry and dispatcher.

All tools self-register by calling `registry.register()`. The orchestrator
calls `registry.get_definitions()` to get provider-formatted tool schemas,
and `registry.dispatch()` to execute a tool by name.
"""

import logging
from typing import Any, Callable, Awaitable

from harness.providers.base import ToolDefinition

logger = logging.getLogger(__name__)

# Type for async tool handlers
ToolHandler = Callable[[dict[str, Any]], Awaitable[str]]


class ToolRegistry:
    """Central registry for all available tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self._handlers: dict[str, ToolHandler] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: ToolHandler,
    ) -> None:
        """Register a tool with its schema and async handler function."""
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
        )
        self._handlers[name] = handler
        logger.debug("Registered tool: %s", name)

    def get_definitions(self) -> list[ToolDefinition]:
        """Return all registered tool definitions (for provider API calls)."""
        return list(self._tools.values())

    async def dispatch(self, name: str, arguments: dict[str, Any]) -> str:
        """
        Execute a tool by name with the given arguments.

        Returns the string result. Raises KeyError if tool not found.
        """
        if name not in self._handlers:
            available = ", ".join(self._tools.keys())
            raise KeyError(f"Unknown tool: {name!r}. Available: {available}")
        handler = self._handlers[name]
        result = await handler(arguments)
        return str(result)

    def list_tools(self) -> list[str]:
        """Return list of registered tool names."""
        return list(self._tools.keys())


def build_default_registry(
    brain_provider: Any = None,
    fast_model: str = "",
    memory_dir: str = "./memory",
) -> ToolRegistry:
    """
    Build and return a ToolRegistry pre-populated with all standard tools.

    `brain_provider` and `fast_model` are needed for the `summarize` and
    `spawn_agent` tools. Pass None to skip those tools.
    """
    from harness.tools.web_search import web_search_handler
    from harness.tools.web_fetch import web_fetch_handler
    from harness.tools.code_exec import python_exec_handler
    from harness.tools.memory import make_memory_handlers
    from harness.tools.agent_builder import make_spawn_agent_handler, make_summarize_handler

    registry = ToolRegistry()

    # --- Web Search ---
    registry.register(
        name="web_search",
        description=(
            "Search the web using DuckDuckGo. Returns a list of results with titles, "
            "URLs, and snippets. Use for finding current information, news, or facts "
            "you don't know from training data."
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 8, max: 20)",
                    "default": 8,
                },
            },
            "required": ["query"],
        },
        handler=web_search_handler,
    )

    # --- Web Fetch ---
    registry.register(
        name="web_fetch",
        description=(
            "Fetch and extract the text content of a web page. Cleans HTML and returns "
            "readable text. Use when you need the full content of a specific URL "
            "(e.g., after finding it via web_search)."
        ),
        parameters={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum characters to return (default: 8000)",
                    "default": 8000,
                },
            },
            "required": ["url"],
        },
        handler=web_fetch_handler,
    )

    # --- Python Execution ---
    registry.register(
        name="python_exec",
        description=(
            "Execute Python code in a sandboxed subprocess. Returns stdout, stderr, "
            "and the return code. Use for calculations, data processing, generating "
            "output, or verifying logic. Has a 30-second timeout."
        ),
        parameters={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Execution timeout in seconds (default: 30, max: 60)",
                    "default": 30,
                },
            },
            "required": ["code"],
        },
        handler=python_exec_handler,
    )

    # --- Memory ---
    memory_save, memory_load = make_memory_handlers(memory_dir)

    registry.register(
        name="memory_save",
        description=(
            "Save a piece of information to persistent memory for a user. "
            "This survives across conversations. Use to remember preferences, "
            "facts the user told you, or work-in-progress state."
        ),
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User identifier (e.g., Telegram user ID)",
                },
                "key": {
                    "type": "string",
                    "description": "Memory key (like a variable name)",
                },
                "value": {
                    "type": "string",
                    "description": "Value to store (will be stored as string)",
                },
            },
            "required": ["user_id", "key", "value"],
        },
        handler=memory_save,
    )

    registry.register(
        name="memory_load",
        description=(
            "Load a piece of information from persistent memory for a user. "
            "Returns the stored value, or null if the key doesn't exist."
        ),
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User identifier (e.g., Telegram user ID)",
                },
                "key": {
                    "type": "string",
                    "description": "Memory key to retrieve (omit to list all keys)",
                },
            },
            "required": ["user_id"],
        },
        handler=memory_load,
    )

    # --- Agent builder and summarize (require brain provider) ---
    if brain_provider is not None and fast_model:
        registry.register(
            name="spawn_agent",
            description=(
                "Spawn a sub-agent with a custom system prompt to handle a specific task. "
                "The sub-agent runs to completion and returns its result. Use for complex "
                "sub-tasks that benefit from specialized instructions or isolation."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task for the sub-agent to perform",
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "Custom system prompt for the sub-agent (optional)",
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use for the sub-agent (optional, defaults to fast model)",
                    },
                },
                "required": ["task"],
            },
            handler=make_spawn_agent_handler(brain_provider, fast_model),
        )

        registry.register(
            name="summarize",
            description=(
                "Summarize a long piece of text using a fast model. "
                "Useful for condensing web pages, documents, or long tool results "
                "before including them in your response."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to summarize",
                    },
                    "instruction": {
                        "type": "string",
                        "description": "Optional summarization instruction (e.g., 'focus on pricing details')",
                    },
                    "max_words": {
                        "type": "integer",
                        "description": "Approximate target length in words (default: 150)",
                        "default": 150,
                    },
                },
                "required": ["text"],
            },
            handler=make_summarize_handler(brain_provider, fast_model),
        )

    return registry
