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

    # Provider API keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

    # Brain configuration
    BRAIN_PROVIDER: str = os.getenv("BRAIN_PROVIDER", "anthropic")  # anthropic | openrouter | hf
    BRAIN_MODEL: str = os.getenv("BRAIN_MODEL", "claude-sonnet-4-6")
    BRAIN_MODE: str = os.getenv("BRAIN_MODE", "native")  # native | tags

    # HuggingFace Inference Router
    HF_DEFAULT_MODEL: str = os.getenv(
        "HF_DEFAULT_MODEL",
        "huihui-ai/DeepSeek-R1-Distill-Qwen-32B-abliterated:featherless-ai",
    )
    HUGGINGFACE_BASE_URL: str = "https://router.huggingface.co/v1"

    # Auxiliary models
    FAST_MODEL: str = os.getenv("FAST_MODEL", "claude-haiku-4-5-20251001")
    ROUTER_MODEL: str = os.getenv("ROUTER_MODEL", "claude-haiku-4-5-20251001")

    # OpenRouter metadata
    OPENROUTER_APP_NAME: str = os.getenv("OPENROUTER_APP_NAME", "AgentHarness")
    OPENROUTER_APP_URL: str = os.getenv("OPENROUTER_APP_URL", "https://github.com/agent-harness")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Agentic loop limits
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "10"))

    # Memory
    MEMORY_DIR: Path = Path(os.getenv("MEMORY_DIR", "./memory"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def validate(self) -> list[str]:
        """Return a list of validation error strings (empty = all good)."""
        errors = []
        if not self.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        if self.BRAIN_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required when BRAIN_PROVIDER=anthropic")
        if self.BRAIN_PROVIDER == "openrouter" and not self.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY is required when BRAIN_PROVIDER=openrouter")
        if self.BRAIN_PROVIDER == "hf" and not self.HF_TOKEN:
            errors.append("HF_TOKEN is required when BRAIN_PROVIDER=hf")
        if self.BRAIN_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when BRAIN_PROVIDER=openai")
        if self.BRAIN_MODE not in ("native", "tags"):
            errors.append(f"BRAIN_MODE must be 'native' or 'tags', got: {self.BRAIN_MODE!r}")
        valid_providers = ("anthropic", "openrouter", "openai", "hf")
        if self.BRAIN_PROVIDER not in valid_providers:
            errors.append(
                f"BRAIN_PROVIDER must be one of {valid_providers}, got: {self.BRAIN_PROVIDER!r}"
            )
        return errors


settings = Settings()
