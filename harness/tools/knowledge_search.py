"""
knowledge_search tool — search the local platform documentation knowledge base.

Walks markdown files under knowledge/ (at repo root), splits them into sections
by ## headers, scores sections by keyword overlap, and returns the top N matches.
"""

import logging
import re
from pathlib import Path

from harness.tools.registry import registry

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "knowledge"


def _score_section(text: str, terms: list[str]) -> int:
    """Count how many times any query term appears in text (case-insensitive)."""
    lower = text.lower()
    return sum(lower.count(term) for term in terms)


def _split_into_sections(content: str) -> list[tuple[str, str]]:
    """
    Split markdown content into (header, body) pairs using ## headings.
    The preamble before the first ## gets header '' (empty string).
    """
    sections: list[tuple[str, str]] = []
    current_header = ""
    current_lines: list[str] = []

    for line in content.splitlines():
        if line.startswith("## "):
            # Flush previous section
            if current_lines or current_header:
                sections.append((current_header, "\n".join(current_lines).strip()))
            current_header = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Flush last section
    if current_lines or current_header:
        sections.append((current_header, "\n".join(current_lines).strip()))

    return sections


@registry.register(
    name="knowledge_search",
    description=(
        "Search the local platform documentation knowledge base for setup guides, "
        "API references, pricing, authentication patterns, and integration tips. "
        "Covers Anthropic, HuggingFace, OpenRouter, OpenAI, AWS Bedrock, Google Cloud "
        "Vertex AI, RunPod, Replit, GitHub Actions, and more. "
        "Use this BEFORE web_search when asked about platform setup, model names, "
        "pricing, or API configuration — it has curated accurate information."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Keywords to search for (e.g. 'anthropic authentication api key', 'runpod serverless endpoint')",
            },
            "platform": {
                "type": "string",
                "description": "Optional: filter to a specific platform (anthropic, huggingface, openai, openrouter, aws, google, runpod, replit, github)",
            },
            "max_results": {
                "type": "integer",
                "description": "Max number of matching sections to return (default 5)",
                "default": 5,
            },
        },
        "required": ["query"],
    },
)
async def knowledge_search(query: str, platform: str = "", max_results: int = 5) -> str:
    """Search local knowledge base markdown files and return top matching sections."""
    max_results = max(1, int(max_results))
    terms = [t.lower() for t in re.split(r"\s+", query.strip()) if t]

    if not terms:
        return "Please provide at least one search term."

    if not KNOWLEDGE_DIR.exists():
        return (
            f"Knowledge base directory not found at {KNOWLEDGE_DIR}. "
            "Run scripts/fetch_docs.py to populate it, or use web_search instead."
        )

    # Determine search root — optionally filter by platform subdirectory
    if platform:
        search_root = KNOWLEDGE_DIR / platform.lower().strip()
        if not search_root.is_dir():
            return (
                f"No knowledge base directory found for platform '{platform}'. "
                f"Available platforms: {', '.join(d.name for d in KNOWLEDGE_DIR.iterdir() if d.is_dir())}. "
                "Try web_search instead."
            )
    else:
        search_root = KNOWLEDGE_DIR

    # Collect all markdown files
    md_files = list(search_root.rglob("*.md"))
    if not md_files:
        return (
            "The knowledge base is empty. "
            "Run scripts/fetch_docs.py to populate it, or use web_search instead."
        )

    # Score every section in every file
    scored: list[tuple[int, str, str, str]] = []  # (score, rel_path, header, body)

    for md_path in md_files:
        try:
            content = md_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            logger.warning("Could not read %s: %s", md_path, exc)
            continue

        rel_path = md_path.relative_to(KNOWLEDGE_DIR)
        sections = _split_into_sections(content)

        for header, body in sections:
            if not body:
                continue
            # Score on header + body together so header matches count more
            combined = f"{header} {header} {body}"  # double header weight
            score = _score_section(combined, terms)
            if score > 0:
                scored.append((score, str(rel_path), header, body))

    if not scored:
        return (
            f"No results found in the knowledge base for: {query}\n"
            "Suggestion: try web_search for up-to-date information."
        )

    # Sort descending by score, take top N
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:max_results]

    parts: list[str] = [f"Knowledge base results for: {query}\n"]
    for score, rel_path, header, body in top:
        label = f"{rel_path} > {header}" if header else rel_path
        # Truncate very long sections
        snippet = body if len(body) <= 2000 else body[:2000] + "\n...[truncated]"
        parts.append(f"--- [{label}] ---\n{snippet}\n")

    return "\n".join(parts)
