"""
Tool registry — central registry for all tools available to the agent.

Tools register themselves via `@registry.register(...)` and are dispatched
by name at runtime. Each tool is a plain async function that accepts keyword
arguments and returns a string result.
"""

import logging
from typing import Any, Callable, Awaitable

from harness.providers.base import ToolDefinition

logger = logging.getLogger(__name__)

# Callable type: async function (kwargs) -> str
ToolFn = Callable[..., Awaitable[str]]


class ToolRegistry:
    """
    Maintains a mapping of tool name → (ToolDefinition, handler function).

    Usage:
        registry = ToolRegistry()

        @registry.register(
            name="web_search",
            description="Search the web",
            parameters={...json schema...},
        )
        async def web_search(query: str) -> str:
            ...
    """

    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolDefinition, ToolFn]] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
    ) -> Callable[[ToolFn], ToolFn]:
        """Decorator that registers an async function as a tool."""

        def decorator(fn: ToolFn) -> ToolFn:
            defn = ToolDefinition(name=name, description=description, parameters=parameters)
            self._tools[name] = (defn, fn)
            logger.debug("Registered tool: %s", name)
            return fn

        return decorator

    def get_definitions(self, subset: list[str] | None = None) -> list[ToolDefinition]:
        """
        Return all registered ToolDefinition objects.

        If `subset` is provided, only return tools whose names are in that list.
        Unknown names in `subset` are silently ignored.
        """
        if subset is None:
            return [defn for defn, _ in self._tools.values()]
        return [
            defn
            for name, (defn, _) in self._tools.items()
            if name in subset
        ]

    def get_names(self) -> list[str]:
        """Return sorted list of all registered tool names."""
        return sorted(self._tools.keys())

    async def dispatch(self, name: str, arguments: dict[str, Any]) -> str:
        """
        Call the named tool with the given arguments.

        Raises KeyError if tool not found.
        Returns a string result (converting non-strings automatically).
        """
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name!r}. Available: {self.get_names()}")
        _, fn = self._tools[name]
        result = await fn(**arguments)
        return str(result)

    def has(self, name: str) -> bool:
        """Return True if a tool with this name is registered."""
        return name in self._tools


# Global singleton registry — import and use everywhere
registry = ToolRegistry()
