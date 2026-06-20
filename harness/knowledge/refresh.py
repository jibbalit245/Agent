"""
Knowledge graph build and nightly refresh pipeline.

Full build:  crawl all URLs from the index files, extract, store.
Refresh:     re-crawl, diff content hash, re-extract only changed pages,
             mark facts from unchanged pages as verified (not stale).

The refresh job can be driven by the scheduler in main.py or run standalone
via scripts/build_knowledge_graph.py.
"""

import asyncio
import logging
from datetime import datetime, timezone

from harness.knowledge import graph_db
from harness.knowledge.crawler import fetch, fetch_batch, CrawlResult
from harness.knowledge.extractor import extract, ExtractionResult
from harness.knowledge.url_parser import extract_urls, SourceEntry

logger = logging.getLogger(__name__)


async def _store_extraction(
    result: ExtractionResult,
    source_url: str,
    source_title: str,
    domain: str,
) -> tuple[int, int]:
    """
    Persist an ExtractionResult into the graph DB.
    Returns (entities_added, facts_added).
    """
    if not result.entities and not result.facts:
        return 0, 0

    # Build entity name → id map
    entity_ids: dict[str, int] = {}
    for ent in result.entities:
        try:
            eid = graph_db.upsert_entity(
                name=ent.name,
                entity_type=ent.entity_type,
                domain=ent.domain,
                description=ent.description,
                canonical=ent.canonical,
                aliases=ent.aliases,
            )
            entity_ids[ent.name] = eid
        except Exception as exc:
            logger.warning("Failed to upsert entity '%s': %s", ent.name, exc)

    facts_stored = 0
    for fact in result.facts:
        eid = entity_ids.get(fact.entity)
        if eid is None:
            # Entity was mentioned in facts but not in entities list — create minimal record
            try:
                eid = graph_db.upsert_entity(
                    name=fact.entity,
                    entity_type="concept",
                    domain=domain,
                )
                entity_ids[fact.entity] = eid
            except Exception:
                continue
        try:
            graph_db.upsert_fact(
                entity_id=eid,
                predicate=fact.predicate,
                value=fact.value,
                source_url=source_url,
                unit=fact.unit,
                as_of_date=fact.as_of_date,
                source_title=source_title,
                confidence=fact.confidence,
            )
            facts_stored += 1
        except Exception as exc:
            logger.warning("Failed to upsert fact %s.%s: %s", fact.entity, fact.predicate, exc)

    for rel in result.relationships:
        from_id = entity_ids.get(rel.from_entity)
        to_id = entity_ids.get(rel.to_entity)
        if from_id and to_id:
            try:
                graph_db.upsert_relationship(
                    from_id=from_id,
                    relation=rel.relation,
                    to_id=to_id,
                    source_url=source_url,
                    context=rel.context,
                    confidence=rel.confidence,
                )
            except Exception as exc:
                logger.warning("Failed to upsert relationship: %s", exc)

    return len(entity_ids), facts_stored


async def process_source(entry: SourceEntry, force: bool = False) -> dict:
    """
    Crawl one source, extract knowledge, store it.
    Returns a status dict for logging.
    """
    # Register source if not already present
    source_id = graph_db.upsert_source(
        url=entry.url,
        domain=entry.domain,
        subtopic=entry.subtopic,
        index_file=entry.index_file,
        description=entry.description,
    )

    # Check existing hash to skip unchanged pages during refresh
    existing = [s for s in graph_db.get_all_sources() if s["id"] == source_id]
    existing_hash = existing[0].get("content_hash", "") if existing else ""

    # Crawl
    crawl = await fetch(entry.url)

    if crawl.status != "ok":
        graph_db.update_source_crawl(
            source_id=source_id,
            status=crawl.status,
            error_message=crawl.error_message,
        )
        return {
            "url": entry.url,
            "status": crawl.status,
            "error": crawl.error_message,
            "entities": 0,
            "facts": 0,
        }

    changed = crawl.content_hash != existing_hash

    if not changed and not force and existing_hash:
        # Content unchanged — just refresh verification timestamps
        graph_db.update_source_crawl(
            source_id=source_id,
            status="ok",
            content_hash=crawl.content_hash,
            content_changed=False,
        )
        return {"url": entry.url, "status": "ok", "changed": False, "entities": 0, "facts": 0}

    # Extract knowledge from content
    extraction = await extract(
        content=crawl.content,
        url=entry.url,
        domain=entry.domain,
        source_title=crawl.title,
    )

    entities_n, facts_n = await _store_extraction(
        result=extraction,
        source_url=entry.url,
        source_title=crawl.title,
        domain=entry.domain,
    )

    graph_db.update_source_crawl(
        source_id=source_id,
        status="ok",
        content_hash=crawl.content_hash,
        facts_extracted=facts_n,
        entities_found=entities_n,
        content_changed=changed,
    )

    return {
        "url": entry.url,
        "status": "ok",
        "changed": changed,
        "entities": entities_n,
        "facts": facts_n,
        "model": extraction.model_used,
    }


async def run_full_build(
    concurrency: int = 4,
    delay: float = 0.8,
    domain_filter: str = "",
    log_every: int = 10,
) -> dict:
    """
    Parse all index files, crawl every URL, extract and store knowledge.

    Args:
        concurrency:   Max simultaneous extractions (not just fetches — each
                       extraction makes an LLM call, so keep this modest)
        delay:         Seconds between starting extractions
        domain_filter: If set, only process URLs from this domain
        log_every:     Log a progress line every N URLs

    Returns summary dict with totals.
    """
    graph_db.init_db()

    entries = extract_urls()
    if domain_filter:
        entries = [e for e in entries if e.domain == domain_filter]

    logger.info(
        "Starting full build: %d URLs%s",
        len(entries),
        f" (domain={domain_filter})" if domain_filter else "",
    )

    semaphore = asyncio.Semaphore(concurrency)
    totals = {"entities": 0, "facts": 0, "ok": 0, "errors": 0, "skipped": 0}
    done = 0

    async def _process(entry: SourceEntry) -> None:
        nonlocal done
        async with semaphore:
            if delay > 0:
                await asyncio.sleep(delay)
            try:
                result = await process_source(entry)
                totals["entities"] += result.get("entities", 0)
                totals["facts"]    += result.get("facts", 0)
                if result["status"] == "ok":
                    totals["ok"] += 1
                elif result["status"] in ("blocked", "skipped"):
                    totals["skipped"] += 1
                else:
                    totals["errors"] += 1
            except Exception as exc:
                logger.error("Unhandled error on %s: %s", entry.url, exc)
                totals["errors"] += 1
            finally:
                done += 1
                if done % log_every == 0 or done == len(entries):
                    logger.info(
                        "Progress: %d/%d | entities=%d facts=%d ok=%d err=%d skip=%d",
                        done, len(entries),
                        totals["entities"], totals["facts"],
                        totals["ok"], totals["errors"], totals["skipped"],
                    )

    await asyncio.gather(*[_process(e) for e in entries])

    stats = graph_db.get_stats()
    logger.info("Build complete. Graph stats: %s", stats)
    totals["graph_stats"] = stats
    return totals


async def run_refresh(concurrency: int = 3, delay: float = 1.0) -> dict:
    """
    Nightly refresh: re-crawl all OK sources, re-extract only changed pages.
    Mark all facts as stale first so unchanged-but-reverified facts get un-staled.
    """
    graph_db.init_db()

    # Pull all registered sources — crawl everything, diff by hash
    sources = graph_db.get_all_sources()
    logger.info("Refresh: %d sources to check", len(sources))

    # Mark everything stale; successful re-crawl will un-stale verified facts
    stale_count = graph_db.mark_stale()
    logger.info("Marked %d facts as stale for refresh", stale_count)

    semaphore = asyncio.Semaphore(concurrency)
    totals = {"changed": 0, "unchanged": 0, "errors": 0, "new_facts": 0}

    async def _refresh_one(source: dict) -> None:
        async with semaphore:
            if delay > 0:
                await asyncio.sleep(delay)
            entry = SourceEntry(
                url=source["url"],
                domain=source["domain"],
                subtopic=source.get("subtopic", ""),
                description=source.get("description", ""),
                index_file=source.get("index_file", ""),
            )
            try:
                result = await process_source(entry)
                if result.get("changed"):
                    totals["changed"] += 1
                    totals["new_facts"] += result.get("facts", 0)
                else:
                    totals["unchanged"] += 1
            except Exception as exc:
                logger.error("Refresh error on %s: %s", source["url"], exc)
                totals["errors"] += 1

    await asyncio.gather(*[_refresh_one(s) for s in sources])

    # Also pick up any new URLs added to index files since last build
    existing_urls = {s["url"] for s in sources}
    all_entries = extract_urls()
    new_entries = [e for e in all_entries if e.url not in existing_urls]
    if new_entries:
        logger.info("Refresh: %d new URLs found in index files", len(new_entries))
        new_semaphore = asyncio.Semaphore(concurrency)
        async def _process_new(entry: SourceEntry) -> None:
            async with new_semaphore:
                if delay > 0:
                    await asyncio.sleep(delay)
                try:
                    result = await process_source(entry)
                    totals["new_facts"] += result.get("facts", 0)
                except Exception as exc:
                    logger.error("New URL error on %s: %s", entry.url, exc)
        await asyncio.gather(*[_process_new(e) for e in new_entries])

    stats = graph_db.get_stats()
    logger.info("Refresh complete: %s | stats: %s", totals, stats)
    totals["graph_stats"] = stats
    return totals
