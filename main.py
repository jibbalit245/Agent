"""
Agent Harness - Main Entry Point

Wires together all components and starts the Telegram bot gateway.

Run with:
    python main.py

Environment variables (see .env.example):
    TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY / OPENROUTER_API_KEY,
    BRAIN_PROVIDER, BRAIN_MODEL, BRAIN_MODE, FAST_MODEL, etc.
"""

import asyncio
import logging
import sys

from config import settings


def setup_logging() -> None:
    """Configure structured logging."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


def build_provider():
    """Instantiate the configured AI provider."""
    from harness.providers.anthropic_provider import AnthropicProvider
    from harness.providers.openrouter import OpenRouterProvider

    provider_name = settings.BRAIN_PROVIDER
    if provider_name == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is required for provider=anthropic")
        return AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
    elif provider_name == "openrouter":
        if not settings.OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY is required for provider=openrouter")
        return OpenRouterProvider(
            api_key=settings.OPENROUTER_API_KEY,
            app_name=settings.OPENROUTER_APP_NAME,
            app_url=settings.OPENROUTER_APP_URL,
        )
    else:
        raise RuntimeError(f"Unknown BRAIN_PROVIDER: {provider_name!r}. Use 'anthropic' or 'openrouter'.")


def build_orchestrator(provider):
    """Build the full orchestrator with all tools registered."""
    from harness.core.brain import Brain
    from harness.core.orchestrator import Orchestrator
    from harness.tools.registry import build_default_registry

    brain = Brain(
        provider=provider,
        model=settings.BRAIN_MODEL,
        mode=settings.BRAIN_MODE,
    )

    tool_registry = build_default_registry(
        brain_provider=provider,
        fast_model=settings.FAST_MODEL,
        memory_dir=str(settings.MEMORY_DIR),
    )

    orchestrator = Orchestrator(
        brain=brain,
        tool_registry=tool_registry,
        max_iterations=settings.MAX_ITERATIONS,
    )

    return orchestrator


def build_router(provider):
    """Build the request router (optional - returns None on failure)."""
    try:
        from harness.core.router import Router
        return Router(
            provider=provider,
            router_model=settings.ROUTER_MODEL,
            brain_model=settings.BRAIN_MODEL,
            fast_model=settings.FAST_MODEL,
        )
    except Exception as exc:
        logging.getLogger(__name__).warning("Failed to build router: %s", exc)
        return None


async def main() -> None:
    """Main async entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Agent Harness starting up")
    logger.info("Provider: %s | Model: %s | Mode: %s", settings.BRAIN_PROVIDER, settings.BRAIN_MODEL, settings.BRAIN_MODE)

    # Validate configuration
    errors = settings.validate()
    if errors:
        for err in errors:
            logger.error("Config error: %s", err)
        sys.exit(1)

    # Build components
    provider = build_provider()
    logger.info("Provider initialized: %s", type(provider).__name__)

    orchestrator = build_orchestrator(provider)
    logger.info("Orchestrator ready with tools: %s", orchestrator.tool_registry.list_tools())

    router = build_router(provider)
    if router:
        logger.info("Router initialized")

    # Start Telegram gateway
    from harness.gateways.telegram import TelegramGateway
    gateway = TelegramGateway(
        token=settings.TELEGRAM_BOT_TOKEN,
        orchestrator=orchestrator,
        router=router,
        settings=settings,
    )

    try:
        await gateway.run()
    except KeyboardInterrupt:
        logger.info("Shutting down")
    except Exception as exc:
        logger.critical("Fatal error: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
