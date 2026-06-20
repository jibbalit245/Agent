"""
Parse all source URLs out of the knowledge/index/*.md files.

For each URL we capture:
  - The URL itself
  - Domain (physics, math, finance, etc.) — inferred from the file name
  - Subtopic — the ## section it appears under
  - Description — the surrounding text line(s) that mention the URL
  - Index file it came from

Deduplicates URLs across files (first occurrence wins for metadata).
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

INDEX_DIR = Path(__file__).parent.parent.parent / "knowledge" / "index"

# Map index filename stem → domain tag used in the graph
_DOMAIN_MAP = {
    "code":        "code",
    "physics":     "physics",
    "chemistry":   "chemistry",
    "finance":     "finance",
    "news":        "news",
    "engineering": "engineering",
    "business":    "business",
    "psychology":  "psychology",
    "marketing":   "marketing",
    "webdesign":   "webdesign",
    "math":        "math",
    "geometry":    "geometry",
    "master":      "cross-domain",
}

# Patterns that are not real crawlable content pages
_SKIP_PATTERNS = [
    r"^https?://localhost",
    r"^https?://127\.",
    r"mailto:",
    r"\.pdf$",           # PDFs need different handling
    r"^https?://doi\.org",  # DOI redirects, too variable
]
_SKIP_RE = re.compile("|".join(_SKIP_PATTERNS), re.IGNORECASE)

_URL_RE = re.compile(r"https?://[^\s\)\]\>\"\']+")


@dataclass
class SourceEntry:
    url: str
    domain: str
    subtopic: str
    description: str
    index_file: str


def _clean_url(url: str) -> str:
    """Strip trailing punctuation that may have been captured."""
    return url.rstrip(".,;:!?)\]>\"'")


def _extract_description(line: str, url: str) -> str:
    """Pull the meaningful text around a URL from its source line."""
    # Remove markdown link syntax: [text](url) → text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", line)
    # Remove bare URL from line
    text = text.replace(url, "").strip()
    # Remove leading markdown symbols
    text = re.sub(r"^[-*#+|>\s]+", "", text).strip()
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text[:300]  # cap description length


def extract_urls(index_dir: Path = INDEX_DIR) -> list[SourceEntry]:
    """
    Parse all index markdown files and return a deduplicated list of SourceEntry.
    Order: physics, chemistry, math, code, finance, engineering, business,
           psychology, marketing, webdesign, geometry, news, master.
    """
    seen: set[str] = set()
    entries: list[SourceEntry] = []

    # Process in a consistent order; master last to avoid clobbering specific domains
    priority = ["physics", "chemistry", "math", "code", "finance", "engineering",
                "business", "psychology", "marketing", "webdesign", "geometry", "news", "master"]

    md_files = {f.stem: f for f in index_dir.glob("*.md")}
    ordered = [md_files[stem] for stem in priority if stem in md_files]
    # append any extra files not in priority list
    ordered += [f for f in md_files.values() if f.stem not in priority]

    for md_path in ordered:
        domain = _DOMAIN_MAP.get(md_path.stem, md_path.stem)
        try:
            content = md_path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Cannot read %s: %s", md_path, exc)
            continue

        current_subtopic = ""
        for line in content.splitlines():
            # Track current ## section as subtopic
            if line.startswith("## "):
                current_subtopic = line[3:].strip()
                continue
            if line.startswith("### "):
                current_subtopic = line[4:].strip()
                continue

            for raw_url in _URL_RE.findall(line):
                url = _clean_url(raw_url)
                if _SKIP_RE.search(url):
                    continue
                if url in seen:
                    continue
                seen.add(url)
                desc = _extract_description(line, raw_url)
                entries.append(SourceEntry(
                    url=url,
                    domain=domain,
                    subtopic=current_subtopic,
                    description=desc,
                    index_file=str(md_path.relative_to(index_dir.parent)),
                ))

    logger.info("URL parser: found %d unique crawlable URLs across %d index files",
                len(entries), len(ordered))
    return entries


def summarize_by_domain(entries: list[SourceEntry]) -> dict[str, int]:
    """Count entries per domain — useful for progress reporting."""
    counts: dict[str, int] = {}
    for e in entries:
        counts[e.domain] = counts.get(e.domain, 0) + 1
    return dict(sorted(counts.items()))
