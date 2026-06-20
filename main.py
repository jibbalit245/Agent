"""
Agent Harness — main entry point.

Wires together:
  - Configuration (from .env)
  - Providers (Anthropic / OpenRouter / HuggingFace)
  - Tool registry (web, python, memory, summarize)
  - Agent registry (loads configs from agent_configs/)
  - Agent manager (creates sessions from configs)
  - Telegram gateway (dispatches messages, handles agent commands)

Run with:
    python main.py
"""

import logging
import sys
from pathlib import Path

from config import settings

# ── Logging setup ──────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
# Reduce noise from third-party libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("anthropic").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ── Validate config ────────────────────────────────────────────────
errors = settings.validate()
if errors:
    for err in errors:
        logger.error("Config error: %s", err)
    sys.exit(1)

# ── Providers ──────────────────────────────────────────────────────
from harness.providers.base import BaseProvider

providers: dict[str, BaseProvider] = {}

if settings.ANTHROPIC_API_KEY:
    from harness.providers.anthropic_provider import AnthropicProvider
    providers["anthropic"] = AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
    logger.info("Anthropic provider initialized")

if settings.OPENROUTER_API_KEY:
    try:
        from harness.providers.openrouter_provider import OpenRouterProvider
        providers["openrouter"] = OpenRouterProvider(
            api_key=settings.OPENROUTER_API_KEY,
            app_name=settings.OPENROUTER_APP_NAME,
            app_url=settings.OPENROUTER_APP_URL,
        )
        logger.info("OpenRouter provider initialized")
    except ImportError:
        logger.warning("OpenRouter provider not available (missing module)")

if settings.OPENAI_API_KEY:
    try:
        from harness.providers.openai_provider import OpenAIProvider
        providers["openai"] = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
        logger.info("OpenAI provider initialized")
    except Exception as exc:
        logger.warning("OpenAI provider failed: %s", exc)

if settings.HF_TOKEN:
    from harness.providers.huggingface_provider import HuggingFaceProvider
    providers["hf"] = HuggingFaceProvider(api_key=settings.HF_TOKEN)
    logger.info("HuggingFace provider initialized")

if not providers:
    logger.error("No providers configured. Set ANTHROPIC_API_KEY, OPENROUTER_API_KEY, or HF_TOKEN.")
    sys.exit(1)

# ── Tool registry ──────────────────────────────────────────────────
# Import tool modules — side-effects register tools into the global registry
import harness.tools.web              # noqa: F401  registers web_search, web_fetch
import harness.tools.python_exec      # noqa: F401  registers python_exec
import harness.tools.memory_tools     # noqa: F401  registers memory_save, memory_load
import harness.tools.summarize        # noqa: F401  registers summarize
import harness.tools.knowledge_search # noqa: F401  registers knowledge_search
import harness.tools.council          # noqa: F401  registers council_consult
import harness.tools.long_context     # noqa: F401  registers long_context_read
import harness.tools.graph_query      # noqa: F401  registers graph_query

from harness.tools.registry import registry as tool_registry
from harness.tools.summarize import set_provider as configure_summarize
from harness.tools.council import set_council_providers
from harness.tools.long_context import set_long_context_provider
from harness.knowledge.extractor import set_extractor_provider
from harness.knowledge import graph_db

# Initialize the graph DB schema (safe no-op if already exists)
graph_db.init_db()

# Wire up the summarize tool with the primary provider
primary_provider = providers.get(settings.BRAIN_PROVIDER) or next(iter(providers.values()))
configure_summarize(primary_provider, settings.FAST_MODEL)

# Wire up the council tool with all available providers
set_council_providers(providers, primary_model=settings.BRAIN_MODEL, fast_model=settings.FAST_MODEL)
logger.info("Council configured with providers: %s", list(providers.keys()))

# Wire up knowledge graph extractor (Haiku for volume, Sonnet for deep passes)
_extractor_provider = providers.get("anthropic") or providers.get("openrouter") or primary_provider
set_extractor_provider(
    provider=_extractor_provider,
    fast_model=settings.FAST_MODEL,
    deep_model=settings.BRAIN_MODEL,
)
logger.info("Knowledge graph extractor ready (fast=%s, deep=%s)", settings.FAST_MODEL, settings.BRAIN_MODEL)

# Wire up Llama Scout long-context tool — prefer openrouter, fall back to hf
_lc_provider_name = settings.LONG_CONTEXT_PROVIDER or (
    "openrouter" if "openrouter" in providers else
    "hf" if "hf" in providers else
    ""
)
if _lc_provider_name and _lc_provider_name in providers:
    _lc_model = (
        settings.LONG_CONTEXT_MODEL_HF
        if _lc_provider_name == "hf"
        else settings.LONG_CONTEXT_MODEL_OPENROUTER
    )
    set_long_context_provider(providers[_lc_provider_name], _lc_model)
    logger.info("Long-context provider: %s / %s", _lc_provider_name, _lc_model)
else:
    logger.info("Long-context tool inactive (no openrouter or hf provider configured)")

# Log graph stats at startup if the DB is populated
try:
    _stats = graph_db.get_stats()
    if _stats["entities"] > 0:
        logger.info(
            "Knowledge graph: %d entities, %d facts, %d relationships",
            _stats["entities"], _stats["facts"], _stats["relationships"],
        )
    else:
        logger.info(
            "Knowledge graph DB exists but is empty. "
            "Run: python scripts/build_knowledge_graph.py"
        )
except Exception:
    pass

logger.info("Tools registered: %s", tool_registry.get_names())

# ── Agent registry ──────────────────────────────────────────────────
from harness.agents.agent_registry import AgentRegistry

agent_registry = AgentRegistry(configs_dir=Path("agent_configs"))
logger.info("Agents loaded: %d", agent_registry.count())

if agent_registry.count() == 0:
    logger.warning("No agents found. Make sure agent_configs/defaults/ exists.")

# ── Agent manager ──────────────────────────────────────────────────
from harness.agents.agent_manager import AgentManager

# Pick the default agent (researcher if available, else first in list)
default_agent_id: str | None = None
if agent_registry.exists("researcher"):
    default_agent_id = "researcher"
elif agent_registry.list_agents():
    default_agent_id = agent_registry.list_agents()[0].id

agent_manager = AgentManager(
    registry=agent_registry,
    tool_registry=tool_registry,
    providers=providers,
    default_agent_id=default_agent_id,
)
logger.info("Agent manager ready. Default agent: %s", default_agent_id)

# ── Telegram gateway ────────────────────────────────────────────────
from harness.gateways.telegram import TelegramBot

bot = TelegramBot(
    token=settings.TELEGRAM_BOT_TOKEN,
    agent_manager=agent_manager,
    agent_registry=agent_registry,
    memory_dir=settings.MEMORY_DIR,
)

# ── Nightly knowledge graph refresh ────────────────────────────────
import asyncio as _asyncio

async def _nightly_refresh_loop() -> None:
    """Re-crawl all sources nightly at 03:00 UTC, extracting only changed pages."""
    import datetime as _dt
    while True:
        now = _dt.datetime.now(_dt.timezone.utc)
        # Next 03:00 UTC
        target = now.replace(hour=3, minute=0, second=0, microsecond=0)
        if target <= now:
            target = target + _dt.timedelta(days=1)
        wait_secs = (target - now).total_seconds()
        logger.info("Knowledge graph refresh scheduled in %.1f hours", wait_secs / 3600)
        await _asyncio.sleep(wait_secs)
        logger.info("Starting nightly knowledge graph refresh...")
        try:
            from harness.knowledge.refresh import run_refresh
            result = await run_refresh(concurrency=2, delay=1.5)
            logger.info("Nightly refresh complete: %s", result)
        except Exception as exc:
            logger.error("Nightly refresh failed: %s", exc, exc_info=True)


# ── Start ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import threading as _threading

    logger.info("Starting Agent Harness...")
    settings.MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    # Run the nightly refresh loop in a background thread with its own event loop
    def _refresh_thread() -> None:
        loop = _asyncio.new_event_loop()
        _asyncio.set_event_loop(loop)
        loop.run_until_complete(_nightly_refresh_loop())

    _t = _threading.Thread(target=_refresh_thread, daemon=True, name="kg-refresh")
    _t.start()

    bot.run()
