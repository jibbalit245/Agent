"""
Async HTTP crawler for knowledge graph seed URLs.

Fetches pages, cleans HTML, computes content hash for change detection.
Respects robots.txt politeness via configurable delay and concurrency limit.
"""

import asyncio
import hashlib
import logging
import re
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_TIMEOUT = 20.0      # seconds per request
_MAX_CONTENT = 15000  # chars to keep for extraction (enough for Haiku context)
_RETRY_DELAYS = [2, 5, 12]  # seconds between retries

_HEADERS = {
    "User-Agent": (
        "AgentHarness-KnowledgeBot/1.0 "
        "(research crawler; contact: agent-harness@example.com)"
    ),
    "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Domains that reliably block bots — mark as skipped rather than erroring
_BLOCKED_DOMAINS = {
    "scholar.harvard.edu",
    "www.springer.com",
    "link.springer.com",
    "www.elsevier.com",
    "www.sciencedirect.com",
    "academic.oup.com",
    "onlinelibrary.wiley.com",
    "afajof.org",
    "jpm.iijournals.com",
    "ieeexplore.ieee.org",
    "dl.acm.org",
    "mathscinet.ams.org",
    "www.msci.com",
    "wrds-www.wharton.upenn.edu",
    "optionmetrics.com",
    "www.cambridge.org",
    "www.comsol.com",
}


@dataclass
class CrawlResult:
    url: str
    status: str           # ok | error | timeout | blocked | skipped
    content: str          # cleaned text (empty on failure)
    title: str            # page <title> if found
    content_hash: str     # SHA256 of raw content (empty on failure)
    error_message: str    # details on failure


def _domain(url: str) -> str:
    from urllib.parse import urlparse
    return urlparse(url).netloc.lower()


def _clean_html(html: str) -> tuple[str, str]:
    """Parse HTML, remove boilerplate, return (title, clean_text)."""
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception:
            return "", re.sub(r"<[^>]+>", " ", html)

    title = ""
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)[:200]

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "form", "button", "noscript", "iframe",
                     "svg", "img", "figure", "figcaption"]):
        tag.decompose()

    # Prefer main content areas
    main = (
        soup.find("main") or
        soup.find("article") or
        soup.find(id=re.compile(r"content|main|body", re.I)) or
        soup.find(class_=re.compile(r"content|main|article", re.I)) or
        soup.body or
        soup
    )

    text = main.get_text(separator="\n", strip=True)
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return title, text


async def fetch(url: str, client: httpx.AsyncClient | None = None) -> CrawlResult:
    """
    Fetch a single URL and return a CrawlResult.

    If `client` is provided it will be reused (caller manages lifecycle).
    Otherwise a fresh client is created and closed after the request.
    """
    dom = _domain(url)
    if dom in _BLOCKED_DOMAINS:
        return CrawlResult(
            url=url, status="blocked", content="", title="",
            content_hash="", error_message=f"Domain {dom} known to block crawlers",
        )

    own_client = client is None
    if own_client:
        client = httpx.AsyncClient(
            timeout=_TIMEOUT,
            follow_redirects=True,
            headers=_HEADERS,
        )

    last_error = ""
    for attempt, delay in enumerate([0] + _RETRY_DELAYS):
        if delay:
            await asyncio.sleep(delay)
        try:
            response = await client.get(url)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", delay * 2 or 10))
                logger.debug("Rate-limited on %s, waiting %ds", url, retry_after)
                await asyncio.sleep(retry_after)
                continue
            response.raise_for_status()

            raw = response.text
            content_hash = hashlib.sha256(raw.encode()).hexdigest()
            content_type = response.headers.get("content-type", "")

            if "html" in content_type or raw.lstrip().startswith("<"):
                title, text = _clean_html(raw)
            else:
                title, text = "", raw.strip()

            if len(text) > _MAX_CONTENT:
                text = text[:_MAX_CONTENT] + f"\n\n[...truncated at {_MAX_CONTENT} chars]"

            return CrawlResult(
                url=url, status="ok", content=text, title=title,
                content_hash=content_hash, error_message="",
            )

        except httpx.TimeoutException:
            last_error = f"Timeout after {_TIMEOUT}s (attempt {attempt + 1})"
            logger.debug("Timeout on %s attempt %d", url, attempt + 1)
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code in (401, 403, 404, 410):
                # Non-retriable errors
                if own_client:
                    await client.aclose()
                return CrawlResult(
                    url=url, status="blocked" if status_code in (401, 403) else "error",
                    content="", title="", content_hash="",
                    error_message=f"HTTP {status_code}",
                )
            last_error = f"HTTP {status_code}"
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            logger.debug("Fetch error on %s: %s", url, exc)

    if own_client:
        await client.aclose()

    return CrawlResult(
        url=url,
        status="timeout" if "Timeout" in last_error else "error",
        content="", title="", content_hash="",
        error_message=last_error,
    )


async def fetch_batch(
    urls: list[str],
    concurrency: int = 5,
    inter_request_delay: float = 0.5,
    progress_callback=None,
) -> list[CrawlResult]:
    """
    Fetch multiple URLs with bounded concurrency.

    Args:
        urls:                  List of URLs to fetch
        concurrency:           Max simultaneous requests
        inter_request_delay:   Seconds to wait between starting requests (politeness)
        progress_callback:     Optional async callable(done, total, result) for progress
    """
    semaphore = asyncio.Semaphore(concurrency)
    results: list[CrawlResult | None] = [None] * len(urls)
    done_count = 0

    async with httpx.AsyncClient(
        timeout=_TIMEOUT,
        follow_redirects=True,
        headers=_HEADERS,
    ) as client:

        async def _fetch_one(idx: int, url: str) -> None:
            nonlocal done_count
            async with semaphore:
                result = await fetch(url, client=client)
                results[idx] = result
                done_count += 1
                if progress_callback:
                    await progress_callback(done_count, len(urls), result)
                if inter_request_delay > 0:
                    await asyncio.sleep(inter_request_delay)

        await asyncio.gather(*[_fetch_one(i, u) for i, u in enumerate(urls)])

    return [r for r in results if r is not None]
