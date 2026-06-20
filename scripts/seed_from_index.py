"""
Seed the knowledge graph directly from the knowledge/index/*.md files.

No API keys required. No crawling required.
Extracts entities and facts from the structured markdown:
  - Entity names from **bold** references, table rows, and header context
  - Descriptions from surrounding prose
  - URLs as available_at / api_base_url facts
  - Authors, publishers, ISBNs where visible
  - Topics covered, subtopics, free/open-access status
  - Relationships: publication covers topic, tool implements algorithm, etc.

This gives the graph an immediately queryable baseline.
The LLM extractor (scripts/build_knowledge_graph.py) runs on top later
to add precise API endpoints, exact constant values, complexity bounds, etc.
"""

import re
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("seed")

from harness.knowledge.graph_db import (
    init_db, upsert_entity, upsert_fact, upsert_relationship,
    upsert_source, get_stats,
)
from harness.knowledge.url_parser import INDEX_DIR, _DOMAIN_MAP

# ── Patterns ──────────────────────────────────────────────────────────────────

_BOLD_RE   = re.compile(r"\*\*(.+?)\*\*")
_URL_RE    = re.compile(r"https?://[^\s\)\]\>\"\']+")
_ISBN_RE   = re.compile(r"\bISBN[-\s]?([\d\-X]{10,17})\b", re.I)
_AUTHOR_RE = re.compile(r"\(([A-Z][a-z]+(?:\s+(?:&|and|et al\.?|[A-Z][a-z]+))*(?:,\s*\d{4})?)\)")
_YEAR_RE   = re.compile(r"\b(19|20)\d{2}\b")
_ED_RE     = re.compile(r"(\d+(?:st|nd|rd|th)\s+ed(?:ition)?\.?)", re.I)
_FREE_RE   = re.compile(r"\bfree\b|\bopen.access\b|\bfree\s+pdf\b|\bfree\s+online\b", re.I)
_API_RE    = re.compile(r"\bAPI\b|\bendpoint\b|\bREST\b|\bJSON\b", re.I)


def _clean(text: str) -> str:
    """Strip markdown syntax and collapse whitespace."""
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # [text](url) → text
    text = re.sub(r"[*_`#|>]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _strip_trailing_punct(url: str) -> str:
    return url.rstrip(".,;:!?)\]>\"'")


def _extract_authors(line: str) -> list[str]:
    """Pull author names from common citation patterns."""
    authors = []
    # "Author — Title" or "Author, Author2 — Title"
    dash_match = re.match(r"^[-*\s]*\*?\*?([A-Z][^\*—–]+?)(?:\s+—|—|\*\*)", line)
    if dash_match:
        raw = dash_match.group(1).strip()
        # Split by & or and
        parts = re.split(r"\s+(?:&|and)\s+", raw)
        authors = [p.strip() for p in parts if len(p.strip()) > 2]

    # Parenthetical: (Griffiths), (Rudin et al., 2022)
    for m in _AUTHOR_RE.finditer(line):
        name = m.group(1).split(",")[0].strip()
        if name and not name.isdigit():
            authors.append(name)
    return list(dict.fromkeys(authors))  # deduplicate, preserve order


def _is_free(line: str) -> bool:
    return bool(_FREE_RE.search(line))


def _has_api(line: str) -> bool:
    return bool(_API_RE.search(line))


# ── Per-domain seed logic ──────────────────────────────────────────────────────

def seed_file(md_path: Path, domain: str) -> dict:
    """Parse one index file and write entities/facts to the graph."""
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    counts = {"entities": 0, "facts": 0, "sources": 0, "relationships": 0}
    current_section = ""
    current_subsection = ""

    # Track entities created in this file for relationship linking
    # name → entity_id
    entity_map: dict[str, int] = {}

    def _ensure_entity(name: str, etype: str, desc: str = "") -> int:
        if name in entity_map:
            return entity_map[name]
        eid = upsert_entity(name=name, entity_type=etype, domain=domain, description=desc)
        entity_map[name] = eid
        counts["entities"] += 1
        return eid

    def _add_fact(eid: int, predicate: str, value: str, unit: str = "", as_of: str = "") -> None:
        if not value.strip():
            return
        upsert_fact(
            entity_id=eid,
            predicate=predicate,
            value=value.strip(),
            source_url=f"knowledge/index/{md_path.name}",
            unit=unit,
            as_of_date=as_of,
            source_title=f"{domain} doctoral index",
            confidence=0.85,  # index-derived, not crawled — slightly lower confidence
        )
        counts["facts"] += 1

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Section tracking
        if stripped.startswith("## "):
            current_section = stripped[3:].strip()
            current_subsection = ""
            i += 1
            continue
        if stripped.startswith("### "):
            current_subsection = stripped[4:].strip()
            i += 1
            continue

        # Skip empty lines, code blocks, table separators
        if not stripped or stripped.startswith("```") or stripped.startswith("|---"):
            i += 1
            continue

        # ── Table rows: | Subtopic | Source | URL | ──────────────────────────
        if stripped.startswith("|") and "|" in stripped[1:]:
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if len(cells) >= 2 and cells[0].lower() not in ("subtopic", "area", "source", "best source", "url", "domain", "file"):
                topic = _clean(cells[0])
                source_name = _clean(cells[1]) if len(cells) > 1 else ""
                url = ""
                for cell in cells:
                    found = _URL_RE.search(cell)
                    if found:
                        url = _strip_trailing_punct(found.group())
                        break

                if topic and len(topic) > 2:
                    eid = _ensure_entity(topic, "concept", f"{topic} — {current_section}")
                    if source_name and source_name != topic:
                        _add_fact(eid, "canonical_source", source_name)
                    if url:
                        _add_fact(eid, "available_at", url)
                        upsert_source(url=url, domain=domain, subtopic=topic,
                                     index_file=str(md_path.name),
                                     description=f"{topic}: {source_name}")
                        counts["sources"] += 1
            i += 1
            continue

        # ── Bullet items with bold entity name ───────────────────────────────
        # Pattern: - **Name** — description
        # or:      - **Name** (Authors) — description
        bold_match = _BOLD_RE.search(stripped)
        if bold_match and (stripped.startswith("-") or stripped.startswith("*") or stripped.startswith("+")):
            entity_name = _clean(bold_match.group(1))
            if not entity_name or len(entity_name) < 2:
                i += 1
                continue

            # Determine entity type from context
            section_lower = (current_section + " " + current_subsection).lower()
            if any(k in section_lower for k in ("textbook", "book", "reference", "foundational", "graduate", "course", "publication")):
                etype = "publication"
            elif any(k in section_lower for k in ("tool", "library", "software", "framework", "api", "computation", "cas")):
                etype = "tool"
            elif any(k in section_lower for k in ("dataset", "data", "database", "preprint", "journal", "venue", "server")):
                etype = "dataset"
            elif any(k in section_lower for k in ("person", "author", "researcher")):
                etype = "person"
            elif any(k in section_lower for k in ("algorithm", "method")):
                etype = "algorithm"
            else:
                # Try to infer from the name itself
                if any(k in entity_name.lower() for k in ("library", "framework", "toolkit", "sdk", "api")):
                    etype = "tool"
                elif any(k in entity_name.lower() for k in ("journal", "review", "proceedings", "arxiv", "ssrn")):
                    etype = "dataset"
                else:
                    etype = "publication" if current_section.lower() in ("foundational textbooks", "textbooks", "graduate textbooks by area") else "concept"

            # Build description from rest of line
            after_bold = stripped[bold_match.end():].strip()
            after_bold = re.sub(r"^[\s—–\-:]+", "", after_bold).strip()
            desc = _clean(after_bold)[:300]

            eid = _ensure_entity(entity_name, etype, desc)

            # Extract authors
            authors = _extract_authors(stripped)
            if authors:
                _add_fact(eid, "authors", ", ".join(authors))

            # Extract year
            year_m = _YEAR_RE.search(stripped)
            if year_m:
                _add_fact(eid, "year", year_m.group())

            # Extract edition
            ed_m = _ED_RE.search(stripped)
            if ed_m:
                _add_fact(eid, "edition", ed_m.group(1))

            # Free/open-access
            if _is_free(stripped):
                _add_fact(eid, "access", "free/open-access")

            # Has API
            if _has_api(stripped):
                _add_fact(eid, "has_api", "yes")

            # ISBN
            for isbn_m in _ISBN_RE.finditer(stripped):
                _add_fact(eid, "isbn", isbn_m.group(1))

            # All URLs in this line
            for raw_url in _URL_RE.findall(stripped):
                url = _strip_trailing_punct(raw_url)
                _add_fact(eid, "available_at", url)
                upsert_source(url=url, domain=domain, subtopic=entity_name,
                             index_file=str(md_path.name), description=desc[:200])
                counts["sources"] += 1

            # Section relationship: entity is part_of / covers the current section
            if current_section:
                _add_fact(eid, "section", current_section)
                if current_subsection:
                    _add_fact(eid, "subsection", current_subsection)

            # Look ahead: next non-empty lines may be continuation description
            j = i + 1
            while j < len(lines) and j < i + 4:
                next_line = lines[j].strip()
                if not next_line or next_line.startswith("#") or next_line.startswith("|") or next_line.startswith("```"):
                    break
                if next_line.startswith("-") or next_line.startswith("*"):
                    break
                # Continuation line — extract any additional URLs
                for raw_url in _URL_RE.findall(next_line):
                    url = _strip_trailing_punct(raw_url)
                    _add_fact(eid, "available_at", url)
                    upsert_source(url=url, domain=domain, subtopic=entity_name,
                                 index_file=str(md_path.name), description=_clean(next_line)[:200])
                    counts["sources"] += 1
                j += 1

            i += 1
            continue

        # ── Bare URL line (reference list) ────────────────────────────────────
        url_m = _URL_RE.search(stripped)
        if url_m and current_section:
            url = _strip_trailing_punct(url_m.group())
            desc = _clean(stripped.replace(url_m.group(), "")).strip()
            if desc and len(desc) > 3:
                # Named resource
                eid = _ensure_entity(desc[:120], "concept", f"{desc} — {current_section}")
                _add_fact(eid, "available_at", url)
                upsert_source(url=url, domain=domain, subtopic=current_section,
                             index_file=str(md_path.name), description=desc[:200])
                counts["sources"] += 1
            i += 1
            continue

        i += 1

    return counts


def run() -> None:
    init_db()
    logger.info("Seeding knowledge graph from index markdown files...")

    priority = ["physics", "chemistry", "math", "code", "finance", "engineering",
                "business", "psychology", "marketing", "webdesign", "geometry", "news", "master"]

    md_files = {f.stem: f for f in INDEX_DIR.glob("*.md")}
    ordered = [md_files[stem] for stem in priority if stem in md_files]
    ordered += [f for f in md_files.values() if f.stem not in priority]

    totals = {"entities": 0, "facts": 0, "sources": 0, "relationships": 0}

    for md_path in ordered:
        domain = _DOMAIN_MAP.get(md_path.stem, md_path.stem)
        logger.info("Processing %s (%s)...", md_path.name, domain)
        try:
            counts = seed_file(md_path, domain)
            logger.info(
                "  → %d entities, %d facts, %d sources",
                counts["entities"], counts["facts"], counts["sources"],
            )
            for k, v in counts.items():
                totals[k] = totals.get(k, 0) + v
        except Exception as exc:
            logger.error("Failed on %s: %s", md_path.name, exc, exc_info=True)

    stats = get_stats()
    print("\n" + "=" * 55)
    print("SEED COMPLETE")
    print(f"  Entities:      {stats['entities']:,}")
    print(f"  Facts:         {stats['facts']:,}")
    print(f"  Relationships: {stats['relationships']:,}")
    print(f"  Sources:       {stats['sources']:,}")
    print("\n  By domain:")
    for domain, count in stats["by_domain"].items():
        print(f"    {domain:<18} {count:>4} entities")
    print()
    print("Next step: run  python scripts/build_knowledge_graph.py")
    print("to crawl each source URL and extract precise facts via LLM.")


if __name__ == "__main__":
    run()
