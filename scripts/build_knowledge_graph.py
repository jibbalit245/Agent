#!/usr/bin/env python3
"""
Seed the knowledge graph from the doctoral index files.

Usage:
    python scripts/build_knowledge_graph.py
    python scripts/build_knowledge_graph.py --domain physics
    python scripts/build_knowledge_graph.py --refresh      # re-crawl all, skip unchanged
    python scripts/build_knowledge_graph.py --stats        # just show current stats

This script performs full build by default:
  1. Parses all 13 knowledge/index/*.md files to extract URLs
  2. Crawls each URL (with politeness delay)
  3. Runs LLM extraction to pull precise entities, facts, relationships
  4. Stores everything in knowledge/knowledge_graph.db

Typical runtime: 30-90 minutes for the full index depending on API rate limits.
Re-running is safe — all writes are upserts. Use --refresh to skip unchanged pages.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add repo root to path so we can import harness
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )
    # Reduce noise
    for name in ("httpx", "httpcore", "anthropic"):
        logging.getLogger(name).setLevel(logging.WARNING)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Build or refresh the knowledge graph")
    parser.add_argument("--domain",   help="Only process URLs from this domain")
    parser.add_argument("--refresh",  action="store_true", help="Refresh mode: skip unchanged pages")
    parser.add_argument("--stats",    action="store_true", help="Print current graph stats and exit")
    parser.add_argument("--concurrency", type=int, default=3, help="Parallel extractions (default 3)")
    parser.add_argument("--delay",    type=float, default=1.0, help="Seconds between requests (default 1.0)")
    args = parser.parse_args()

    _setup_logging()
    logger = logging.getLogger("build_graph")

    # Initialize providers
    from harness.providers.base import BaseProvider
    providers: dict[str, BaseProvider] = {}

    if settings.ANTHROPIC_API_KEY:
        from harness.providers.anthropic_provider import AnthropicProvider
        providers["anthropic"] = AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
        logger.info("Using Anthropic provider")
    elif settings.OPENAI_API_KEY:
        from harness.providers.openai_provider import OpenAIProvider
        providers["openai"] = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
        logger.info("Using OpenAI provider")
    elif settings.MOONSHOT_API_KEY:
        from harness.providers.moonshot_provider import MoonshotProvider
        providers["moonshot"] = MoonshotProvider(
            api_key=settings.MOONSHOT_API_KEY,
            base_url=settings.MOONSHOT_BASE_URL,
        )
        logger.info("Using Moonshot provider")
    else:
        logger.error("No provider configured. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or MOONSHOT_API_KEY.")
        sys.exit(1)

    provider = next(iter(providers.values()))

    # Wire extractor
    from harness.knowledge.extractor import set_extractor_provider
    set_extractor_provider(
        provider=provider,
        fast_model=settings.FAST_MODEL,
        deep_model=settings.BRAIN_MODEL,
    )

    from harness.knowledge import graph_db
    graph_db.init_db()

    if args.stats:
        stats = graph_db.get_stats()
        print("\nKnowledge Graph Statistics")
        print("=" * 40)
        print(f"Entities:         {stats['entities']:,}")
        print(f"Facts (fresh):    {stats['facts']:,}")
        print(f"Facts (stale):    {stats['stale_facts']:,}")
        print(f"Relationships:    {stats['relationships']:,}")
        print(f"Sources crawled:  {stats['sources_ok']:,} / {stats['sources']:,}")
        print("\nEntities by domain:")
        for domain, count in stats["by_domain"].items():
            print(f"  {domain:<20} {count:>5}")
        return

    if args.refresh:
        logger.info("Running refresh (re-crawl + diff)...")
        from harness.knowledge.refresh import run_refresh
        totals = await run_refresh(
            concurrency=args.concurrency,
            delay=args.delay,
        )
    else:
        logger.info("Running full build...")
        from harness.knowledge.refresh import run_full_build
        totals = await run_full_build(
            concurrency=args.concurrency,
            delay=args.delay,
            domain_filter=args.domain or "",
        )

    print("\n" + "=" * 50)
    print("DONE")
    print(f"  Entities stored:  {totals.get('entities', 0):,}")
    print(f"  Facts stored:     {totals.get('facts', 0):,}")
    print(f"  OK:               {totals.get('ok', 0):,}")
    print(f"  Errors:           {totals.get('errors', 0):,}")
    print(f"  Skipped/blocked:  {totals.get('skipped', 0):,}")

    stats = graph_db.get_stats()
    print(f"\n  Total in graph:")
    print(f"    Entities:       {stats['entities']:,}")
    print(f"    Facts:          {stats['facts']:,}")
    print(f"    Relationships:  {stats['relationships']:,}")


if __name__ == "__main__":
    asyncio.run(main())
