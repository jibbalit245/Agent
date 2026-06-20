"""
SQLite knowledge graph — entities, typed relationships, precise atomic facts.

Schema design priorities:
  - Every fact carries source URL + extraction timestamp so staleness is trackable
  - Relationships are typed ("authored_by", "requires", "proves", "costs", etc.)
  - Content hashing on sources enables change detection for the nightly refresh
  - All writes are upserts so the build script is safely re-runnable
"""

import hashlib
import json
import logging
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "knowledge" / "knowledge_graph.db"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _conn():
    """Thread-local SQLite connection with WAL mode for concurrent reads."""
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init_db() -> None:
    """Create all tables and indices. Safe to call on an existing database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _conn() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS entities (
            id            INTEGER PRIMARY KEY,
            name          TEXT NOT NULL,
            canonical     TEXT,          -- normalized / preferred form
            entity_type   TEXT NOT NULL, -- concept | person | institution | publication | tool | dataset | constant | algorithm | formula
            domain        TEXT NOT NULL, -- physics | math | code | finance | chemistry | engineering | business | psychology | marketing | webdesign | geometry | news
            description   TEXT,          -- 1-3 sentence precise description
            aliases       TEXT,          -- JSON array of alternate names
            first_seen    TEXT NOT NULL,
            last_updated  TEXT NOT NULL,
            UNIQUE(name, entity_type)
        );

        CREATE TABLE IF NOT EXISTS facts (
            id            INTEGER PRIMARY KEY,
            entity_id     INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
            predicate     TEXT NOT NULL,  -- what kind of fact: value | formula | url | date | count | cost | complexity | prerequisite | etc.
            value         TEXT NOT NULL,  -- THE SPECIFIC VALUE — must be precise, not vague
            unit          TEXT,           -- m/s | tokens | USD/MTok | years | etc.
            as_of_date    TEXT,           -- when this fact was true (for time-sensitive facts)
            source_url    TEXT NOT NULL,
            source_title  TEXT,
            extracted_at  TEXT NOT NULL,
            last_verified TEXT,
            is_stale      INTEGER NOT NULL DEFAULT 0,
            confidence    REAL NOT NULL DEFAULT 1.0,
            UNIQUE(entity_id, predicate, value)
        );

        CREATE TABLE IF NOT EXISTS relationships (
            id            INTEGER PRIMARY KEY,
            from_id       INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
            relation      TEXT NOT NULL,  -- authored_by | published_in | requires | proves | extends | contradicts | implements | cites | costs | available_at | successor_of | part_of | derived_from | covers | defines
            to_id         INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
            context       TEXT,           -- the sentence that establishes this relationship
            confidence    REAL NOT NULL DEFAULT 1.0,
            source_url    TEXT NOT NULL,
            extracted_at  TEXT NOT NULL,
            last_verified TEXT,
            UNIQUE(from_id, relation, to_id)
        );

        CREATE TABLE IF NOT EXISTS sources (
            id              INTEGER PRIMARY KEY,
            url             TEXT UNIQUE NOT NULL,
            domain          TEXT NOT NULL,
            subtopic        TEXT,
            index_file      TEXT,          -- which knowledge/index/*.md file referenced this
            description     TEXT,          -- description from the index file
            last_crawled    TEXT,
            content_hash    TEXT,          -- SHA256 of last fetched content
            crawl_status    TEXT,          -- ok | error | timeout | blocked | skipped
            error_message   TEXT,
            facts_extracted INTEGER NOT NULL DEFAULT 0,
            entities_found  INTEGER NOT NULL DEFAULT 0,
            added_at        TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS crawl_log (
            id                INTEGER PRIMARY KEY,
            source_id         INTEGER NOT NULL REFERENCES sources(id),
            crawled_at        TEXT NOT NULL,
            status            TEXT NOT NULL,
            content_changed   INTEGER NOT NULL DEFAULT 0,
            facts_added       INTEGER NOT NULL DEFAULT 0,
            facts_updated     INTEGER NOT NULL DEFAULT 0,
            entities_added    INTEGER NOT NULL DEFAULT 0,
            error_message     TEXT
        );

        -- Performance indices
        CREATE INDEX IF NOT EXISTS idx_facts_entity    ON facts(entity_id);
        CREATE INDEX IF NOT EXISTS idx_facts_predicate ON facts(predicate);
        CREATE INDEX IF NOT EXISTS idx_facts_stale     ON facts(is_stale);
        CREATE INDEX IF NOT EXISTS idx_rels_from       ON relationships(from_id);
        CREATE INDEX IF NOT EXISTS idx_rels_to         ON relationships(to_id);
        CREATE INDEX IF NOT EXISTS idx_rels_relation   ON relationships(relation);
        CREATE INDEX IF NOT EXISTS idx_entities_domain ON entities(domain);
        CREATE INDEX IF NOT EXISTS idx_entities_type   ON entities(entity_type);
        CREATE INDEX IF NOT EXISTS idx_entities_name   ON entities(name COLLATE NOCASE);
        CREATE INDEX IF NOT EXISTS idx_sources_domain  ON sources(domain);
        CREATE INDEX IF NOT EXISTS idx_sources_status  ON sources(crawl_status);
        """)
    logger.info("Knowledge graph DB initialized at %s", DB_PATH)


# ── Upsert helpers ─────────────────────────────────────────────────────────────

def upsert_entity(
    name: str,
    entity_type: str,
    domain: str,
    description: str = "",
    canonical: str = "",
    aliases: list[str] | None = None,
) -> int:
    """Insert or update an entity. Returns entity ID."""
    now = _now()
    aliases_json = json.dumps(aliases or [])
    with _conn() as con:
        cur = con.execute(
            """
            INSERT INTO entities (name, canonical, entity_type, domain, description, aliases, first_seen, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name, entity_type) DO UPDATE SET
                description  = CASE WHEN excluded.description != '' THEN excluded.description ELSE description END,
                canonical    = CASE WHEN excluded.canonical != '' THEN excluded.canonical ELSE canonical END,
                aliases      = excluded.aliases,
                last_updated = excluded.last_updated
            RETURNING id
            """,
            (name, canonical or name, entity_type, domain, description, aliases_json, now, now),
        )
        row = cur.fetchone()
        return row[0]


def upsert_fact(
    entity_id: int,
    predicate: str,
    value: str,
    source_url: str,
    unit: str = "",
    as_of_date: str = "",
    source_title: str = "",
    confidence: float = 1.0,
) -> None:
    """Insert or update a fact. Resets is_stale=0 on update (fresh data)."""
    now = _now()
    with _conn() as con:
        con.execute(
            """
            INSERT INTO facts (entity_id, predicate, value, unit, as_of_date, source_url, source_title, extracted_at, last_verified, is_stale, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            ON CONFLICT(entity_id, predicate, value) DO UPDATE SET
                unit          = excluded.unit,
                as_of_date    = CASE WHEN excluded.as_of_date != '' THEN excluded.as_of_date ELSE as_of_date END,
                last_verified = excluded.extracted_at,
                is_stale      = 0,
                confidence    = excluded.confidence
            """,
            (entity_id, predicate, value, unit, as_of_date, source_url, source_title, now, now, confidence),
        )


def upsert_relationship(
    from_id: int,
    relation: str,
    to_id: int,
    source_url: str,
    context: str = "",
    confidence: float = 1.0,
) -> None:
    """Insert or update a relationship edge."""
    now = _now()
    with _conn() as con:
        con.execute(
            """
            INSERT INTO relationships (from_id, relation, to_id, context, confidence, source_url, extracted_at, last_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(from_id, relation, to_id) DO UPDATE SET
                context       = CASE WHEN excluded.context != '' THEN excluded.context ELSE context END,
                last_verified = excluded.extracted_at,
                confidence    = excluded.confidence
            """,
            (from_id, relation, to_id, context, confidence, source_url, now, now),
        )


def upsert_source(
    url: str,
    domain: str,
    subtopic: str = "",
    index_file: str = "",
    description: str = "",
) -> int:
    """Register a source URL. Returns source ID."""
    now = _now()
    with _conn() as con:
        cur = con.execute(
            """
            INSERT INTO sources (url, domain, subtopic, index_file, description, crawl_status, added_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
            ON CONFLICT(url) DO UPDATE SET
                domain      = excluded.domain,
                subtopic    = CASE WHEN excluded.subtopic != '' THEN excluded.subtopic ELSE subtopic END,
                description = CASE WHEN excluded.description != '' THEN excluded.description ELSE description END
            RETURNING id
            """,
            (url, domain, subtopic, index_file, description, now),
        )
        return cur.fetchone()[0]


def update_source_crawl(
    source_id: int,
    status: str,
    content_hash: str = "",
    facts_extracted: int = 0,
    entities_found: int = 0,
    error_message: str = "",
    content_changed: bool = False,
) -> None:
    """Update crawl result on a source and write a crawl_log entry."""
    now = _now()
    with _conn() as con:
        con.execute(
            """
            UPDATE sources SET
                last_crawled    = ?,
                content_hash    = CASE WHEN ? != '' THEN ? ELSE content_hash END,
                crawl_status    = ?,
                error_message   = ?,
                facts_extracted = facts_extracted + ?,
                entities_found  = entities_found  + ?
            WHERE id = ?
            """,
            (now, content_hash, content_hash, status, error_message,
             facts_extracted, entities_found, source_id),
        )
        source = con.execute("SELECT id FROM sources WHERE id = ?", (source_id,)).fetchone()
        if source:
            con.execute(
                """
                INSERT INTO crawl_log (source_id, crawled_at, status, content_changed, facts_added, entities_added, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (source_id, now, status, int(content_changed), facts_extracted, entities_found, error_message),
            )


def mark_stale(domain: str | None = None) -> int:
    """Mark facts as stale (before a refresh run). Returns count marked."""
    with _conn() as con:
        if domain:
            cur = con.execute(
                """
                UPDATE facts SET is_stale = 1
                WHERE entity_id IN (SELECT id FROM entities WHERE domain = ?)
                """,
                (domain,),
            )
        else:
            cur = con.execute("UPDATE facts SET is_stale = 1")
        return cur.rowcount


# ── Query helpers ──────────────────────────────────────────────────────────────

def get_entity(name: str) -> dict | None:
    """Fuzzy entity lookup — exact match first, then case-insensitive."""
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM entities WHERE name = ? OR canonical = ? LIMIT 1",
            (name, name),
        ).fetchone()
        if not row:
            row = con.execute(
                "SELECT * FROM entities WHERE name LIKE ? OR canonical LIKE ? LIMIT 1",
                (f"%{name}%", f"%{name}%"),
            ).fetchone()
        return dict(row) if row else None


def get_entity_facts(entity_id: int, include_stale: bool = False) -> list[dict]:
    with _conn() as con:
        q = "SELECT * FROM facts WHERE entity_id = ?"
        if not include_stale:
            q += " AND is_stale = 0"
        q += " ORDER BY predicate"
        return [dict(r) for r in con.execute(q, (entity_id,)).fetchall()]


def get_entity_relationships(entity_id: int) -> list[dict]:
    """Return all relationships where this entity is from OR to."""
    with _conn() as con:
        rows = con.execute(
            """
            SELECT r.relation, r.context, r.confidence, r.source_url,
                   ef.name AS from_name, ef.entity_type AS from_type,
                   et.name AS to_name,   et.entity_type AS to_type
            FROM relationships r
            JOIN entities ef ON r.from_id = ef.id
            JOIN entities et ON r.to_id   = et.id
            WHERE r.from_id = ? OR r.to_id = ?
            ORDER BY r.relation
            """,
            (entity_id, entity_id),
        ).fetchall()
        return [dict(r) for r in rows]


def search_entities(query: str, domain: str = "", limit: int = 10) -> list[dict]:
    """Keyword search across name, canonical, description, and alias fields."""
    with _conn() as con:
        like = f"%{query}%"
        base = """
            SELECT e.*, GROUP_CONCAT(f.predicate || ': ' || f.value, ' | ') AS fact_summary
            FROM entities e
            LEFT JOIN facts f ON f.entity_id = e.id AND f.is_stale = 0
            WHERE (e.name LIKE ? OR e.canonical LIKE ? OR e.description LIKE ? OR e.aliases LIKE ?)
        """
        params: list[Any] = [like, like, like, like]
        if domain:
            base += " AND e.domain = ?"
            params.append(domain)
        base += " GROUP BY e.id ORDER BY e.name LIMIT ?"
        params.append(limit)
        return [dict(r) for r in con.execute(base, params).fetchall()]


def search_facts(predicate: str = "", domain: str = "", limit: int = 20) -> list[dict]:
    """Return facts matching a predicate pattern across a domain."""
    with _conn() as con:
        q = """
            SELECT f.predicate, f.value, f.unit, f.as_of_date, f.source_url,
                   f.confidence, e.name AS entity_name, e.domain
            FROM facts f
            JOIN entities e ON f.entity_id = e.id
            WHERE f.is_stale = 0
        """
        params: list[Any] = []
        if predicate:
            q += " AND f.predicate LIKE ?"
            params.append(f"%{predicate}%")
        if domain:
            q += " AND e.domain = ?"
            params.append(domain)
        q += " ORDER BY e.name, f.predicate LIMIT ?"
        params.append(limit)
        return [dict(r) for r in con.execute(q, params).fetchall()]


def get_stats() -> dict:
    """Return graph statistics."""
    with _conn() as con:
        stats = {}
        stats["entities"]      = con.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        stats["facts"]         = con.execute("SELECT COUNT(*) FROM facts WHERE is_stale = 0").fetchone()[0]
        stats["relationships"] = con.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
        stats["sources"]       = con.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
        stats["sources_ok"]    = con.execute("SELECT COUNT(*) FROM sources WHERE crawl_status = 'ok'").fetchone()[0]
        stats["stale_facts"]   = con.execute("SELECT COUNT(*) FROM facts WHERE is_stale = 1").fetchone()[0]
        by_domain = con.execute(
            "SELECT domain, COUNT(*) AS n FROM entities GROUP BY domain ORDER BY n DESC"
        ).fetchall()
        stats["by_domain"] = {r["domain"]: r["n"] for r in by_domain}
        return stats


def get_pending_sources(limit: int = 0) -> list[dict]:
    """Return sources not yet successfully crawled."""
    with _conn() as con:
        q = "SELECT * FROM sources WHERE crawl_status != 'ok' ORDER BY domain, added_at"
        if limit:
            q += f" LIMIT {limit}"
        return [dict(r) for r in con.execute(q).fetchall()]


def get_all_sources(domain: str = "") -> list[dict]:
    """Return all registered sources, optionally filtered by domain."""
    with _conn() as con:
        if domain:
            rows = con.execute("SELECT * FROM sources WHERE domain = ? ORDER BY domain", (domain,)).fetchall()
        else:
            rows = con.execute("SELECT * FROM sources ORDER BY domain").fetchall()
        return [dict(r) for r in rows]
