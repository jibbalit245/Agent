#!/usr/bin/env python3
"""
fetch_docs.py — refresh the local knowledge base from official platform docs.

Usage:
    python scripts/fetch_docs.py                  # fetch all platforms
    python scripts/fetch_docs.py --platform anthropic
    python scripts/fetch_docs.py --platform openai --platform runpod

Requirements:
    pip install httpx beautifulsoup4 lxml

The script saves cleaned markdown to knowledge/<platform>/<slug>.md.
Each file starts with a header showing the source URL and fetch date.
"""

import argparse
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

# ── Dependencies (graceful import error) ───────────────────────────────────────
try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError as _e:
    print(f"Missing dependency: {_e}")
    print("Install with: pip install httpx beautifulsoup4 lxml")
    sys.exit(1)

# ── Configuration ──────────────────────────────────────────────────────────────
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"
FETCH_TIMEOUT = 20.0  # seconds
MAX_CONTENT_CHARS = 50_000
USER_AGENT = "AgentHarness-DocFetcher/1.0 (knowledge base builder)"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Source URLs ────────────────────────────────────────────────────────────────
# Map platform name → list of documentation URLs to fetch.
# Add or remove URLs here to control what ends up in the knowledge base.
SOURCES: dict[str, list[str]] = {
    "anthropic": [
        "https://docs.anthropic.com/en/docs/about-claude/models",
        "https://docs.anthropic.com/en/docs/get-started",
        "https://docs.anthropic.com/en/api/getting-started",
        "https://docs.anthropic.com/en/docs/about-claude/pricing",
        "https://docs.anthropic.com/en/docs/build-with-claude/rate-limits",
        "https://docs.anthropic.com/en/docs/build-with-claude/tool-use",
        "https://docs.anthropic.com/en/docs/build-with-claude/embeddings",
    ],
    "huggingface": [
        "https://huggingface.co/docs/hub/security-tokens",
        "https://huggingface.co/docs/inference-providers/getting-started",
        "https://huggingface.co/docs/hub/models-the-hub",
        "https://huggingface.co/docs/hub/spaces-overview",
        "https://huggingface.co/docs/huggingface_hub/quick-start",
        "https://huggingface.co/pricing",
    ],
    "openai": [
        "https://platform.openai.com/docs/quickstart",
        "https://platform.openai.com/docs/models",
        "https://platform.openai.com/docs/guides/authentication",
        "https://platform.openai.com/docs/guides/rate-limits",
        "https://openai.com/api/pricing/",
    ],
    "openrouter": [
        "https://openrouter.ai/docs/quick-start",
        "https://openrouter.ai/docs/api-reference/overview",
        "https://openrouter.ai/docs/models",
        "https://openrouter.ai/docs/provider-routing",
        "https://openrouter.ai/docs/limits",
    ],
    "aws": [
        "https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html",
        "https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html",
        "https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html",
        "https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-runtime_example_bedrock-runtime_InvokeModel_AnthropicClaude_section.html",
        "https://aws.amazon.com/bedrock/pricing/",
    ],
    "google": [
        "https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal",
        "https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models",
        "https://cloud.google.com/vertex-ai/generative-ai/pricing",
        "https://ai.google.dev/gemini-api/docs/quickstart",
        "https://ai.google.dev/gemini-api/docs/models/gemini",
        "https://ai.google.dev/gemini-api/docs/api-key",
    ],
    "runpod": [
        "https://docs.runpod.io/get-started/overview",
        "https://docs.runpod.io/serverless/get-started",
        "https://docs.runpod.io/serverless/endpoints/get-started",
        "https://docs.runpod.io/pods/choose-a-pod",
        "https://www.runpod.io/pricing",
    ],
    "replit": [
        "https://docs.replit.com/getting-started/intro-replit",
        "https://docs.replit.com/replit-workspace/configuring-repl",
        "https://docs.replit.com/hosting/deployments/about-deployments",
        "https://docs.replit.com/replit-workspace/secrets",
        "https://replit.com/pricing",
    ],
    "github": [
        "https://docs.github.com/en/actions/writing-workflows/quickstart",
        "https://docs.github.com/en/actions/using-github-hosted-runners/using-github-hosted-runners",
        "https://docs.github.com/en/codespaces/overview",
        "https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration",
        "https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions",
        "https://github.com/marketplace/models",
    ],
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def url_to_slug(url: str) -> str:
    """Convert a URL to a safe filename slug."""
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_") or "index"
    # Remove unsafe characters
    slug = re.sub(r"[^\w\-]", "_", path)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug[:80] or "index"


def html_to_markdown(html: str, url: str) -> str:
    """
    Convert HTML to clean text / pseudo-markdown.
    Preserves heading structure so knowledge_search can split on ## headers.
    """
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    # Remove boilerplate elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                     "noscript", "iframe", "form", "button"]):
        tag.decompose()

    # Convert headings to markdown-style
    for level in range(1, 7):
        prefix = "#" * level
        for h in soup.find_all(f"h{level}"):
            text = h.get_text(" ", strip=True)
            h.replace_with(f"\n\n{prefix} {text}\n\n")

    # Convert code blocks
    for pre in soup.find_all("pre"):
        code_text = pre.get_text()
        pre.replace_with(f"\n```\n{code_text}\n```\n")

    # Convert inline code
    for code in soup.find_all("code"):
        code.replace_with(f"`{code.get_text()}`")

    # Convert links to text (keep URL)
    for a in soup.find_all("a", href=True):
        link_text = a.get_text(strip=True)
        href = a["href"]
        if href.startswith("http"):
            a.replace_with(f"{link_text} ({href})")
        else:
            a.replace_with(link_text)

    text = soup.get_text(separator="\n", strip=True)

    # Normalize whitespace
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = text.strip()

    if len(text) > MAX_CONTENT_CHARS:
        text = text[:MAX_CONTENT_CHARS] + "\n\n[...content truncated by fetch_docs.py]"

    return text


def fetch_url(url: str) -> str | None:
    """Fetch a URL and return cleaned text, or None on failure."""
    try:
        with httpx.Client(
            timeout=FETCH_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            html = response.text
    except httpx.HTTPStatusError as exc:
        logger.warning("HTTP %d fetching %s", exc.response.status_code, url)
        return None
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None

    if "html" in content_type or html.lstrip().startswith("<"):
        return html_to_markdown(html, url)
    return html  # plain text / JSON — return as-is


def save_doc(platform: str, url: str, content: str) -> Path:
    """Save fetched content to knowledge/<platform>/<slug>.md."""
    platform_dir = KNOWLEDGE_DIR / platform
    platform_dir.mkdir(parents=True, exist_ok=True)

    slug = url_to_slug(url)
    out_path = platform_dir / f"{slug}.md"

    fetch_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = (
        f"<!-- source: {url} -->\n"
        f"<!-- fetched: {fetch_date} -->\n\n"
    )

    out_path.write_text(header + content, encoding="utf-8")
    return out_path


# ── Main ───────────────────────────────────────────────────────────────────────

def fetch_platform(platform: str) -> tuple[int, int]:
    """
    Fetch all URLs for a platform.
    Returns (success_count, failure_count).
    """
    urls = SOURCES.get(platform)
    if not urls:
        logger.error("Unknown platform: %s. Available: %s", platform, ", ".join(SOURCES))
        return 0, 0

    success = 0
    failure = 0
    logger.info("Fetching %d URLs for platform '%s'...", len(urls), platform)

    for url in urls:
        logger.info("  GET %s", url)
        content = fetch_url(url)
        if content is None:
            logger.warning("  SKIP (fetch failed): %s", url)
            failure += 1
            continue

        out_path = save_doc(platform, url, content)
        logger.info("  SAVED → %s", out_path.relative_to(KNOWLEDGE_DIR.parent))
        success += 1

    return success, failure


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch and refresh the local platform documentation knowledge base.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--platform",
        action="append",
        dest="platforms",
        metavar="PLATFORM",
        help=(
            "Platform(s) to fetch. Can be specified multiple times. "
            f"Choices: {', '.join(sorted(SOURCES))}. "
            "Omit to fetch all platforms."
        ),
    )
    args = parser.parse_args()

    platforms = args.platforms or list(SOURCES.keys())

    # Validate
    unknown = [p for p in platforms if p not in SOURCES]
    if unknown:
        logger.error("Unknown platform(s): %s. Available: %s", unknown, list(SOURCES))
        sys.exit(1)

    total_success = 0
    total_failure = 0

    for platform in platforms:
        s, f = fetch_platform(platform)
        total_success += s
        total_failure += f

    logger.info(
        "Done. %d page(s) saved, %d failure(s).",
        total_success,
        total_failure,
    )
    if total_failure > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
