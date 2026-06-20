"""
Web search tool using DuckDuckGo.

Uses the duckduckgo_search library which requires no API key.
Returns formatted search results with title, URL, and snippet.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def web_search_handler(args: dict[str, Any]) -> str:
    """
    Search DuckDuckGo and return formatted results.

    Args:
        query: Search query string
        max_results: Max number of results (default 8, capped at 20)
    """
    import asyncio
    from duckduckgo_search import DDGS

    query: str = args.get("query", "")
    max_results: int = min(int(args.get("max_results", 8)), 20)

    if not query:
        return "Error: 'query' argument is required"

    logger.debug("web_search: query=%r, max_results=%d", query, max_results)

    try:
        # duckduckgo_search is synchronous; run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, _search_sync, query, max_results)
    except Exception as exc:
        logger.error("web_search failed: %s", exc, exc_info=True)
        return f"Search failed: {type(exc).__name__}: {exc}"

    if not results:
        return f"No results found for: {query!r}"

    lines = [f"Search results for: {query!r}\n"]
    for i, r in enumerate(results, 1):
        title = r.get("title", "No title")
        url = r.get("href", r.get("url", ""))
        snippet = r.get("body", r.get("snippet", ""))
        lines.append(f"{i}. **{title}**")
        lines.append(f"   URL: {url}")
        if snippet:
            # Truncate long snippets
            snippet = snippet[:300] + "..." if len(snippet) > 300 else snippet
            lines.append(f"   {snippet}")
        lines.append("")

    return "\n".join(lines)


def _search_sync(query: str, max_results: int) -> list[dict]:
    """Synchronous DuckDuckGo search (called via executor)."""
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))
