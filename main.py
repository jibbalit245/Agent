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

from harness.tools.registry import registry as tool_registry
from harness.tools.summarize import set_provider as configure_summarize

# Wire up the summarize tool with the primary provider
primary_provider = providers.get(settings.BRAIN_PROVIDER) or next(iter(providers.values()))
configure_summarize(primary_provider, settings.FAST_MODEL)

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

# ── Start ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting Agent Harness...")
    settings.MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    bot.run()
