"""
Web tools: web_search and web_fetch.

web_search  — DuckDuckGo text search, returns top N results as text.
web_fetch   — Fetch a URL and return readable text content (strips HTML).
"""

import logging
from typing import Any

import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from harness.tools.registry import registry

logger = logging.getLogger(__name__)

_DEFAULT_MAX_RESULTS = 5
_FETCH_TIMEOUT = 15.0  # seconds
_MAX_CONTENT_CHARS = 8000


@registry.register(
    name="web_search",
    description=(
        "Search the web using DuckDuckGo and return the top results. "
        "Use this for current events, facts, or anything you're not sure about."
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
                "description": "Maximum number of results to return (default 5, max 10)",
                "default": _DEFAULT_MAX_RESULTS,
            },
        },
        "required": ["query"],
    },
)
async def web_search(query: str, max_results: int = _DEFAULT_MAX_RESULTS) -> str:
    """Search the web via DuckDuckGo and return formatted results."""
    max_results = min(int(max_results), 10)
    logger.info("web_search: %r (max_results=%d)", query, max_results)

    try:
        with DDGS() as ddgs:
            results: list[dict[str, Any]] = list(ddgs.text(query, max_results=max_results))
    except Exception as exc:
        logger.error("DuckDuckGo search failed: %s", exc)
        return f"Search failed: {exc}"

    if not results:
        return f"No results found for: {query}"

    lines = [f"Search results for: {query}\n"]
    for i, r in enumerate(results, 1):
        title = r.get("title", "No title")
        href = r.get("href", "")
        body = r.get("body", "").strip()
        lines.append(f"{i}. **{title}**")
        if href:
            lines.append(f"   URL: {href}")
        if body:
            # Truncate long snippets
            snippet = body[:300] + ("..." if len(body) > 300 else "")
            lines.append(f"   {snippet}")
        lines.append("")

    return "\n".join(lines)


@registry.register(
    name="web_fetch",
    description=(
        "Fetch the content of a URL and return its readable text. "
        "Use this to read articles, documentation, or any web page."
    ),
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The full URL to fetch (must include http:// or https://)",
            },
            "max_chars": {
                "type": "integer",
                "description": f"Maximum characters to return (default {_MAX_CONTENT_CHARS})",
                "default": _MAX_CONTENT_CHARS,
            },
        },
        "required": ["url"],
    },
)
async def web_fetch(url: str, max_chars: int = _MAX_CONTENT_CHARS) -> str:
    """Fetch a URL and return cleaned text content."""
    logger.info("web_fetch: %s", url)
    max_chars = min(int(max_chars), 20000)

    try:
        async with httpx.AsyncClient(
            timeout=_FETCH_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "AgentHarness/1.0 (research bot)"},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            html = response.text
    except httpx.HTTPStatusError as exc:
        return f"HTTP {exc.response.status_code} error fetching {url}"
    except Exception as exc:
        logger.error("web_fetch failed for %s: %s", url, exc)
        return f"Failed to fetch {url}: {exc}"

    # Parse HTML and extract readable text
    if "html" in content_type or html.lstrip().startswith("<"):
        try:
            soup = BeautifulSoup(html, "lxml")
            # Remove script and style elements
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
        except Exception:
            text = html
    else:
        text = html  # Plain text or JSON

    # Collapse excessive whitespace
    import re
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    if len(text) > max_chars:
        text = text[:max_chars] + f"\n\n[...truncated at {max_chars} chars]"

    return f"Content from {url}:\n\n{text}"
