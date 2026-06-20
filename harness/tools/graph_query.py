"""
graph_query — structured query interface to the knowledge graph.

Complements knowledge_search (which scans flat markdown) with precise,
sourced, dated facts extracted from the actual source pages.

Query modes:
  entity   — everything known about a named entity (facts + relationships)
  domain   — all facts in a domain, optionally filtered by predicate
  search   — keyword search across entity names, descriptions, and fact values
  stats    — graph statistics (entities, facts, coverage by domain)
"""

import logging

from harness.knowledge import graph_db
from harness.tools.registry import registry

logger = logging.getLogger(__name__)


def _format_facts(facts: list[dict]) -> str:
    if not facts:
        return "  (no facts stored)"
    lines = []
    for f in facts:
        val = f["value"]
        if f.get("unit"):
            val = f"{val} {f['unit']}"
        if f.get("as_of_date"):
            val = f"{val}  [as of {f['as_of_date']}]"
        conf = f.get("confidence", 1.0)
        conf_str = f" (confidence: {conf:.0%})" if conf < 0.9 else ""
        lines.append(f"  {f['predicate']}: {val}{conf_str}")
        lines.append(f"    ↳ source: {f['source_url']}")
    return "\n".join(lines)


def _format_relationships(rels: list[dict], focal_entity: str) -> str:
    if not rels:
        return "  (no relationships stored)"
    lines = []
    for r in rels:
        if r["from_name"] == focal_entity:
            lines.append(f"  {r['from_name']} --[{r['relation']}]--> {r['to_name']}")
        else:
            lines.append(f"  {r['from_name']} --[{r['relation']}]--> {r['to_name']}")
        if r.get("context"):
            lines.append(f"    context: \"{r['context'][:200]}\"")
    return "\n".join(lines)


@registry.register(
    name="graph_query",
    description=(
        "Query the local knowledge graph for precise, sourced, dated facts extracted "
        "from 150+ doctoral-level sources across physics, math, code, finance, chemistry, "
        "engineering, business, psychology, marketing, web design, and geometry. "
        "Returns specific values, formulas, API details, complexity bounds, publication info, "
        "and typed relationships — not summaries. "
        "Use this before web_search when you need precise factual claims with provenance. "
        "Modes: 'entity' (everything about X), 'domain' (all facts in a field), "
        "'search' (keyword across graph), 'stats' (graph coverage overview)."
    ),
    parameters={
        "type": "object",
        "properties": {
            "mode": {
                "type": "string",
                "enum": ["entity", "domain", "search", "stats"],
                "description": (
                    "'entity' — full profile of a named entity. "
                    "'domain' — browse facts in a domain. "
                    "'search' — keyword search across all entities and facts. "
                    "'stats'  — graph statistics and coverage."
                ),
            },
            "query": {
                "type": "string",
                "description": (
                    "For entity: the entity name (e.g. 'Black-Scholes', 'FRED', 'QuickSort'). "
                    "For domain: the domain name (physics|math|code|finance|chemistry|engineering|"
                    "business|psychology|marketing|webdesign|geometry|news). "
                    "For search: keywords to search (e.g. 'quantum harmonic oscillator eigenvalue'). "
                    "For stats: leave empty."
                ),
            },
            "predicate_filter": {
                "type": "string",
                "description": (
                    "For domain mode only: filter facts by predicate type "
                    "(e.g. 'formula', 'api_base_url', 'cost', 'complexity_time'). "
                    "Leave empty to return all predicates."
                ),
            },
            "limit": {
                "type": "integer",
                "description": "Max results to return (default 20).",
            },
        },
        "required": ["mode"],
    },
)
async def graph_query(
    mode: str,
    query: str = "",
    predicate_filter: str = "",
    limit: int = 20,
    **kwargs,
) -> str:
    limit = max(1, min(int(limit), 100))

    # Check if the DB exists at all
    from harness.knowledge.graph_db import DB_PATH
    if not DB_PATH.exists():
        return (
            "Knowledge graph database not found. "
            "Run `python scripts/build_knowledge_graph.py` to seed it from the doctoral index."
        )

    try:
        stats = graph_db.get_stats()
    except Exception as exc:
        return f"Knowledge graph unavailable: {exc}"

    if stats["entities"] == 0:
        return (
            "Knowledge graph is empty. "
            "Run `python scripts/build_knowledge_graph.py` to seed it."
        )

    # ── Stats mode ────────────────────────────────────────────────────────────
    if mode == "stats":
        lines = [
            "## Knowledge Graph Coverage\n",
            f"Entities:      {stats['entities']:,}",
            f"Facts:         {stats['facts']:,}  ({stats['stale_facts']:,} stale)",
            f"Relationships: {stats['relationships']:,}",
            f"Sources:       {stats['sources_ok']:,}/{stats['sources']:,} crawled OK",
            "",
            "### Entities by domain",
        ]
        for domain, count in stats["by_domain"].items():
            lines.append(f"  {domain:<16} {count:>5}")
        return "\n".join(lines)

    # ── Entity mode ───────────────────────────────────────────────────────────
    if mode == "entity":
        if not query:
            return "Please provide an entity name for entity mode."
        entity = graph_db.get_entity(query)
        if not entity:
            # Fall through to search to suggest alternatives
            results = graph_db.search_entities(query, limit=5)
            if results:
                suggestions = ", ".join(r["name"] for r in results)
                return (
                    f"No exact entity '{query}' found in the graph.\n"
                    f"Similar entities: {suggestions}\n"
                    "Try graph_query with mode='search' or one of the names above."
                )
            return (
                f"No entity '{query}' found in the knowledge graph. "
                "The graph may not yet have been seeded — run build_knowledge_graph.py."
            )

        facts = graph_db.get_entity_facts(entity["id"])
        rels = graph_db.get_entity_relationships(entity["id"])

        aliases = entity.get("aliases", "[]")
        try:
            import json
            alias_list = json.loads(aliases)
        except Exception:
            alias_list = []

        lines = [
            f"## {entity['name']}",
            f"Type: {entity['entity_type']} | Domain: {entity['domain']}",
        ]
        if entity.get("canonical") and entity["canonical"] != entity["name"]:
            lines.append(f"Canonical: {entity['canonical']}")
        if alias_list:
            lines.append(f"Also known as: {', '.join(alias_list)}")
        if entity.get("description"):
            lines.append(f"\n{entity['description']}")
        lines.append(f"\n### Facts ({len(facts)})")
        lines.append(_format_facts(facts))
        if rels:
            lines.append(f"\n### Relationships ({len(rels)})")
            lines.append(_format_relationships(rels, entity["name"]))
        lines.append(f"\n_Last updated: {entity.get('last_updated', 'unknown')}_")
        return "\n".join(lines)

    # ── Domain mode ───────────────────────────────────────────────────────────
    if mode == "domain":
        if not query:
            return "Please provide a domain name for domain mode."
        facts = graph_db.search_facts(predicate=predicate_filter, domain=query, limit=limit)
        if not facts:
            return (
                f"No facts found for domain='{query}'"
                + (f" predicate='{predicate_filter}'" if predicate_filter else "")
                + ".\nValid domains: physics, math, code, finance, chemistry, engineering, "
                  "business, psychology, marketing, webdesign, geometry, news"
            )
        lines = [
            f"## Domain: {query}"
            + (f" | Predicate: {predicate_filter}" if predicate_filter else ""),
            f"{len(facts)} facts\n",
        ]
        current_entity = None
        for f in facts:
            if f["entity_name"] != current_entity:
                current_entity = f["entity_name"]
                lines.append(f"\n**{current_entity}**")
            val = f["value"]
            if f.get("unit"):
                val = f"{val} {f['unit']}"
            if f.get("as_of_date"):
                val = f"{val} [{f['as_of_date']}]"
            lines.append(f"  {f['predicate']}: {val}")
            lines.append(f"    ↳ {f['source_url']}")
        return "\n".join(lines)

    # ── Search mode ───────────────────────────────────────────────────────────
    if mode == "search":
        if not query:
            return "Please provide keywords for search mode."
        entities = graph_db.search_entities(query, limit=limit)
        if not entities:
            return (
                f"No entities matching '{query}' found in the knowledge graph.\n"
                "The graph may be empty — run build_knowledge_graph.py to seed it."
            )
        lines = [f"## Search results for: {query}\n"]
        for ent in entities:
            lines.append(f"**{ent['name']}** ({ent['entity_type']}, {ent['domain']})")
            if ent.get("description"):
                lines.append(f"  {ent['description'][:200]}")
            if ent.get("fact_summary"):
                lines.append(f"  Facts: {ent['fact_summary'][:300]}")
            lines.append("")
        return "\n".join(lines)

    return f"Unknown mode: {mode}. Valid modes: entity, domain, search, stats"
