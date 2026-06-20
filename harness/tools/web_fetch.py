"""
Web fetch tool using httpx + BeautifulSoup4.

Fetches a URL, strips HTML boilerplate, and returns clean readable text.
Handles redirects, timeouts, and common encodings gracefully.
"""

import logging
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Tags to completely remove (scripts, styles, nav, etc.)
_REMOVE_TAGS = {
    "script", "style", "nav", "header", "footer", "aside",
    "noscript", "iframe", "svg", "form", "button",
    "advertisement", "ads",
}

# Common browser-like headers to avoid basic bot blocking
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


async def web_fetch_handler(args: dict[str, Any]) -> str:
    """
    Fetch a URL and return cleaned text content.

    Args:
        url: URL to fetch
        max_chars: Maximum characters to return (default 8000)
    """
    url: str = args.get("url", "")
    max_chars: int = int(args.get("max_chars", 8000))

    if not url:
        return "Error: 'url' argument is required"

    # Ensure URL has scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    logger.debug("web_fetch: url=%r, max_chars=%d", url, max_chars)

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(20.0),
            headers=_HEADERS,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return f"HTTP error {exc.response.status_code} fetching {url}"
    except httpx.RequestError as exc:
        return f"Request failed for {url}: {type(exc).__name__}: {exc}"

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type and "text/plain" not in content_type:
        return f"Unsupported content type: {content_type} for {url}"

    html = response.text
    text = _extract_text(html, url)

    if len(text) > max_chars:
        text = text[:max_chars] + f"\n\n[Content truncated at {max_chars} characters]"

    return text


def _extract_text(html: str, url: str) -> str:
    """Parse HTML and extract meaningful text content."""
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted tags
    for tag_name in _REMOVE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Try to find main content area
    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id=re.compile(r"content|main|article", re.I))
        or soup.find(class_=re.compile(r"content|main|article|post", re.I))
        or soup.find("body")
        or soup
    )

    # Extract text with reasonable spacing
    text = main_content.get_text(separator="\n", strip=True)

    # Clean up excessive whitespace
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    # Collapse runs of 3+ blank lines to 2
    result = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))

    # Prepend URL for context
    return f"Content from {url}:\n\n{result}"
