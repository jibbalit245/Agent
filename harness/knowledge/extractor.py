"""
LLM-based knowledge extraction from crawled web content.

The extraction prompt is deliberately demanding about specificity.
"Vague" facts are worse than no facts — they crowd out precise ones.

Uses the fast/cheap model (Haiku) for volume, Sonnet for pages where
initial extraction yielded < 3 facts (a signal the page has more depth).
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from harness.providers.base import Message

logger = logging.getLogger(__name__)

# Injected at startup via set_extractor_provider()
_provider: Any = None
_fast_model: str = "claude-haiku-4-5-20251001"
_deep_model: str = "claude-sonnet-4-6"


def set_extractor_provider(provider: Any, fast_model: str, deep_model: str) -> None:
    global _provider, _fast_model, _deep_model
    _provider = provider
    _fast_model = fast_model
    _deep_model = deep_model


@dataclass
class ExtractedEntity:
    name: str
    entity_type: str   # concept | person | institution | publication | tool | dataset | constant | algorithm | formula
    domain: str
    description: str
    canonical: str = ""
    aliases: list[str] = field(default_factory=list)


@dataclass
class ExtractedFact:
    entity: str        # entity name this fact is about
    predicate: str     # what kind of fact: value | formula | url | date | count | cost | complexity | rate_limit | etc.
    value: str         # THE SPECIFIC VALUE — precise, not vague
    unit: str = ""
    as_of_date: str = ""
    confidence: float = 1.0


@dataclass
class ExtractedRelationship:
    from_entity: str
    relation: str      # authored_by | published_in | requires | proves | extends | contradicts | implements | cites | costs | available_at | successor_of | part_of | derived_from | covers | defines
    to_entity: str
    context: str = ""  # the sentence that establishes this
    confidence: float = 1.0


@dataclass
class ExtractionResult:
    entities: list[ExtractedEntity] = field(default_factory=list)
    facts: list[ExtractedFact] = field(default_factory=list)
    relationships: list[ExtractedRelationship] = field(default_factory=list)
    model_used: str = ""
    raw_response: str = ""


_EXTRACTION_SYSTEM = """You are a precision knowledge extraction engine. Your output populates a structured knowledge graph used by AI agents for doctoral-level research.

MISSION: Extract SPECIFIC, VERIFIABLE, PRECISE facts. Vague facts are ACTIVELY HARMFUL — they pollute the graph. If you cannot be specific, omit the fact entirely.

━━━ WHAT COUNTS AS SPECIFIC ━━━

REJECTED (too vague):
  - "FRED contains economic data"
  - "arXiv is a preprint server"
  - "Griffiths is a standard QM textbook"
  - "NIST provides physical constants"

ACCEPTED (specific):
  - "FRED: 800,000+ time series, API endpoint https://api.stlouisfed.org/fred/series/observations, requires free API key, rate limit 120 req/min"
  - "arXiv cs.LG (Machine Learning): https://arxiv.org/list/cs.LG/recent, accepts submissions in PDF/LaTeX, no peer review"
  - "Griffiths QM: Introduction to Quantum Mechanics, 2nd ed 2004, ISBN 0131118927, 480pp, covers Schrödinger eq → perturbation theory → identical particles"
  - "NIST: speed of light c = 299,792,458 m/s (exact, CODATA 2018), Planck constant h = 6.62607015×10⁻³⁴ J·s (exact, CODATA 2018)"

━━━ ENTITY TYPES ━━━
  concept       — mathematical, physical, or theoretical idea (e.g., "Ito calculus", "Black-Scholes model")
  person        — author, researcher, scientist (e.g., "Richard Feynman", "Fischer Black")
  institution   — university, lab, organization (e.g., "MIT CSAIL", "Federal Reserve Bank of St. Louis")
  publication   — textbook, paper, journal (e.g., "Pattern Recognition and Machine Learning", "Journal of Finance")
  tool          — software, library, framework (e.g., "QuantLib", "NumPy", "SageMath")
  dataset       — data source, database, repository (e.g., "FRED", "ImageNet", "Semantic Scholar")
  constant      — physical or mathematical constant (e.g., "speed of light c", "Euler's number e")
  algorithm     — named algorithm or method (e.g., "QuickSort", "Expectation-Maximization", "ADAM optimizer")
  formula       — named equation or law (e.g., "Black-Scholes equation", "Navier-Stokes equations")

━━━ FACT PREDICATES (use these exact strings where applicable) ━━━
  value              — numeric value of a constant or measurement
  formula            — mathematical formula or equation
  url                — a specific endpoint, page, or resource URL
  api_base_url       — base URL for an API
  api_auth           — authentication method (API key, OAuth, none)
  rate_limit         — API rate limit (requests per minute/day)
  release_date       — publication or release date
  version            — software/dataset version number
  isbn               — book ISBN
  doi                — paper DOI
  cost               — pricing information
  count              — number of items (papers, series, rows, etc.)
  complexity_time    — big-O time complexity
  complexity_space   — big-O space complexity
  prerequisite       — what knowledge/tool is required
  covers             — what topics/chapters this publication covers (specific)
  start_date         — when a time series or dataset begins
  frequency          — data update frequency (daily, monthly, quarterly)
  language           — programming language or human language
  license            — software or content license
  institution        — the home institution
  authors            — author list
  year               — publication year
  edition            — edition number

━━━ RELATIONSHIP TYPES ━━━
  authored_by    | published_in  | requires      | proves
  extends        | contradicts   | implements    | cites
  costs          | available_at  | successor_of  | part_of
  derived_from   | covers        | defines       | maintained_by
  available_via  | peer_reviewed_by

━━━ OUTPUT FORMAT ━━━
Return ONLY valid JSON. No markdown, no explanation, no code fences.

{
  "entities": [
    {
      "name": "exact canonical name",
      "entity_type": "one of the types above",
      "domain": "physics|math|code|finance|chemistry|engineering|business|psychology|marketing|webdesign|geometry|news",
      "description": "1-2 sentences, specific — include key distinguishing facts",
      "canonical": "preferred short form if different from name",
      "aliases": ["alternate name 1", "alternate name 2"]
    }
  ],
  "facts": [
    {
      "entity": "entity name from entities list above",
      "predicate": "predicate string",
      "value": "THE SPECIFIC VALUE — exact, not approximate unless uncertainty is real",
      "unit": "unit string or empty string",
      "as_of_date": "YYYY-MM-DD or YYYY or empty string",
      "confidence": 0.0-1.0
    }
  ],
  "relationships": [
    {
      "from": "entity name",
      "relation": "relation type",
      "to": "entity name",
      "context": "the sentence or phrase establishing this relationship",
      "confidence": 0.0-1.0
    }
  ]
}

Extract as many SPECIFIC facts as you can find. A page with 30 precise facts is better than one with 5 vague ones.
Both entities in a relationship MUST appear in your entities list."""


async def extract(
    content: str,
    url: str,
    domain: str,
    source_title: str = "",
    deep: bool = False,
) -> ExtractionResult:
    """
    Run LLM extraction on a crawled page.

    Args:
        content:      Cleaned text content of the page (up to ~12k chars)
        url:          Source URL (for provenance)
        domain:       Domain tag (physics, math, etc.)
        source_title: Page title if available
        deep:         If True, use the deeper model regardless of content size
    """
    if _provider is None:
        logger.warning("Extractor provider not set — skipping extraction for %s", url)
        return ExtractionResult()

    model = _deep_model if deep else _fast_model

    user_msg = (
        f"SOURCE URL: {url}\n"
        f"DOMAIN: {domain}\n"
        f"TITLE: {source_title or 'unknown'}\n\n"
        f"CONTENT:\n{content[:12000]}"
    )

    try:
        result = await _provider.complete(
            model=model,
            messages=[Message(role="user", content=user_msg)],
            system=_EXTRACTION_SYSTEM,
            temperature=0.1,  # low temperature for factual extraction
            max_tokens=4096,
        )
    except Exception as exc:
        logger.error("Extraction API call failed for %s: %s", url, exc)
        return ExtractionResult()

    raw = result.get("text", "").strip()

    # Strip markdown code fences if the model wrapped output anyway
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw.strip())

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.warning("JSON parse failed for %s (%s): %s", url, model, exc)
        # Try to salvage partial JSON by finding the outermost { ... }
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return ExtractionResult(raw_response=raw, model_used=model)
        else:
            return ExtractionResult(raw_response=raw, model_used=model)

    entities = [
        ExtractedEntity(
            name=e.get("name", "").strip(),
            entity_type=e.get("entity_type", "concept"),
            domain=e.get("domain", domain),
            description=e.get("description", ""),
            canonical=e.get("canonical", ""),
            aliases=e.get("aliases", []),
        )
        for e in data.get("entities", [])
        if e.get("name", "").strip()
    ]

    facts = [
        ExtractedFact(
            entity=f.get("entity", "").strip(),
            predicate=f.get("predicate", "").strip(),
            value=str(f.get("value", "")).strip(),
            unit=str(f.get("unit", "")),
            as_of_date=str(f.get("as_of_date", "")),
            confidence=float(f.get("confidence", 1.0)),
        )
        for f in data.get("facts", [])
        if f.get("entity", "").strip() and f.get("value", "").strip()
    ]

    relationships = [
        ExtractedRelationship(
            from_entity=r.get("from", "").strip(),
            relation=r.get("relation", "").strip(),
            to_entity=r.get("to", "").strip(),
            context=r.get("context", ""),
            confidence=float(r.get("confidence", 1.0)),
        )
        for r in data.get("relationships", [])
        if r.get("from", "").strip() and r.get("to", "").strip()
    ]

    # If very few facts on first pass, retry with the deeper model
    if not deep and len(facts) < 3 and model != _deep_model:
        logger.debug("Shallow extraction on %s (%d facts) — retrying with deep model", url, len(facts))
        return await extract(content, url, domain, source_title, deep=True)

    logger.debug(
        "Extracted from %s: %d entities, %d facts, %d relationships (model=%s)",
        url, len(entities), len(facts), len(relationships), model,
    )
    return ExtractionResult(
        entities=entities,
        facts=facts,
        relationships=relationships,
        model_used=model,
        raw_response=raw,
    )
