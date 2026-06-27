"""
Central configuration module. All settings come from environment variables
(loaded from .env by python-dotenv). Import `settings` everywhere you need config.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (same dir as this file)
load_dotenv(Path(__file__).parent / ".env")


class Settings:
    """Singleton-style settings object. All values read from env at import time."""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # Provider API keys — Anthropic, OpenAI, Moonshot (Kimi)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MOONSHOT_API_KEY: str = os.getenv("MOONSHOT_API_KEY", "")

    # Brain configuration
    BRAIN_PROVIDER: str = os.getenv("BRAIN_PROVIDER", "anthropic")  # anthropic | openai | moonshot
    BRAIN_MODEL: str = os.getenv("BRAIN_MODEL", "claude-sonnet-4-6")
    BRAIN_MODE: str = os.getenv("BRAIN_MODE", "native")  # native | tags

    # Moonshot (Kimi) base URL — use api.moonshot.cn/v1 for the China endpoint
    MOONSHOT_BASE_URL: str = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")

    # Auxiliary models
    FAST_MODEL: str = os.getenv("FAST_MODEL", "claude-haiku-4-5-20251001")
    ROUTER_MODEL: str = os.getenv("ROUTER_MODEL", "claude-haiku-4-5-20251001")

    # Long-context model — Kimi K2.6 (256K token context window)
    # Provider must be "moonshot" (the only large-context provider in this set).
    LONG_CONTEXT_MODEL: str = os.getenv("LONG_CONTEXT_MODEL", "kimi-k2.6")

    # Council member model overrides (used by council_consult)
    COUNCIL_GPT_MODEL: str = os.getenv("COUNCIL_GPT_MODEL", "gpt-4o")
    COUNCIL_KIMI_MODEL: str = os.getenv("COUNCIL_KIMI_MODEL", "kimi-k2.6")

    # Kimi K2.6 Agent Swarm (server-side multi-agent decomposition)
    SWARM_MODEL: str = os.getenv("SWARM_MODEL", "kimi-k2.6")
    SWARM_MAX_AGENTS: int = int(os.getenv("SWARM_MAX_AGENTS", "50"))  # default budget; hard cap 300

    # OpenClaw gateway (WebSocket server the OpenClaw phone app connects to)
    OPENCLAW_GATEWAY_ENABLED: bool = os.getenv("OPENCLAW_GATEWAY_ENABLED", "false").lower() in ("1", "true", "yes", "on")
    OPENCLAW_GATEWAY_HOST: str = os.getenv("OPENCLAW_GATEWAY_HOST", "0.0.0.0")
    OPENCLAW_GATEWAY_PORT: int = int(os.getenv("OPENCLAW_GATEWAY_PORT", "18789"))
    OPENCLAW_GATEWAY_TOKEN: str = os.getenv("OPENCLAW_GATEWAY_TOKEN", "")

    # Agentic loop limits
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "10"))

    # Memory
    MEMORY_DIR: Path = Path(os.getenv("MEMORY_DIR", "./memory"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def validate(self) -> list[str]:
        """Return a list of validation error strings (empty = all good)."""
        errors = []
        if not self.TELEGRAM_BOT_TOKEN and not self.OPENCLAW_GATEWAY_ENABLED:
            errors.append("Set TELEGRAM_BOT_TOKEN, or enable OPENCLAW_GATEWAY_ENABLED, to have at least one gateway")
        if self.BRAIN_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required when BRAIN_PROVIDER=anthropic")
        if self.BRAIN_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when BRAIN_PROVIDER=openai")
        if self.BRAIN_PROVIDER == "moonshot" and not self.MOONSHOT_API_KEY:
            errors.append("MOONSHOT_API_KEY is required when BRAIN_PROVIDER=moonshot")
        if self.BRAIN_MODE not in ("native", "tags"):
            errors.append(f"BRAIN_MODE must be 'native' or 'tags', got: {self.BRAIN_MODE!r}")
        valid_providers = ("anthropic", "openai", "moonshot")
        if self.BRAIN_PROVIDER not in valid_providers:
            errors.append(
                f"BRAIN_PROVIDER must be one of {valid_providers}, got: {self.BRAIN_PROVIDER!r}"
            )
        return errors


settings = Settings()
