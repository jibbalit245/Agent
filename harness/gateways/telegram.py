"""
Telegram bot gateway for the agent harness.

Uses python-telegram-bot v20+ (async). Features:
  - Per-user conversation history (in-memory)
  - /start, /clear, /model, /status commands
  - Typing indicator while processing
  - Markdown formatting in responses
  - Error reporting back to user
  - Graceful shutdown

Usage:
    gateway = TelegramGateway(token=..., orchestrator=..., settings=...)
    await gateway.run()
"""

import asyncio
import logging
from typing import Any

from telegram import Update, BotCommand
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import TelegramError

from harness.core.orchestrator import Orchestrator
from harness.core.router import Router
from harness.providers.base import Message
from config import Settings

logger = logging.getLogger(__name__)

# Per-user conversation history: {user_id: [Message, ...]}
_conversation_history: dict[int, list[Message]] = {}

# Per-user model override: {user_id: model_string}
_user_models: dict[int, str] = {}

MAX_HISTORY_MESSAGES = 40  # Keep last N messages per user
MAX_TELEGRAM_MESSAGE = 4096  # Telegram's character limit per message


class TelegramGateway:
    """
    Telegram bot gateway.

    Connects Telegram updates to the Orchestrator. Maintains per-user
    conversation history and handles all Telegram-specific formatting.
    """

    def __init__(
        self,
        token: str,
        orchestrator: Orchestrator,
        router: Router | None,
        settings: Settings,
    ) -> None:
        self.token = token
        self.orchestrator = orchestrator
        self.router = router
        self.settings = settings
        self._app: Application | None = None

    async def run(self) -> None:
        """Build and start the Telegram bot (blocking until stopped)."""
        logger.info("Starting Telegram bot")
        app = (
            Application.builder()
            .token(self.token)
            .build()
        )
        self._app = app

        # Register command handlers
        app.add_handler(CommandHandler("start", self._handle_start))
        app.add_handler(CommandHandler("clear", self._handle_clear))
        app.add_handler(CommandHandler("model", self._handle_model))
        app.add_handler(CommandHandler("status", self._handle_status))
        app.add_handler(CommandHandler("help", self._handle_help))

        # Register message handler (all non-command text)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

        # Set bot commands for Telegram menu
        await app.bot.set_my_commands([
            BotCommand("start", "Start a conversation"),
            BotCommand("clear", "Clear conversation history"),
            BotCommand("model", "Show or change the current model"),
            BotCommand("status", "Show system status"),
            BotCommand("help", "Show help"),
        ])

        logger.info("Bot initialized. Starting polling...")
        async with app:
            await app.start()
            await app.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
            )
            # Run until interrupted
            stop_event = asyncio.Event()
            try:
                await stop_event.wait()
            except (KeyboardInterrupt, asyncio.CancelledError):
                logger.info("Shutdown signal received")
            finally:
                await app.updater.stop()
                await app.stop()

    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        user_id = user.id if user else 0

        _conversation_history.pop(user_id, None)

        name = user.first_name if user else "there"
        await update.message.reply_text(
            f"Hey {name}! I'm your AI assistant with web search, code execution, "
            f"memory, and more.\n\n"
            f"Just talk to me naturally — I'll figure out what tools to use.\n\n"
            f"Commands: /clear /model /status /help",
            parse_mode=ParseMode.MARKDOWN,
        )

    async def _handle_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /clear command - reset conversation history."""
        user_id = update.effective_user.id if update.effective_user else 0
        count = len(_conversation_history.get(user_id, []))
        _conversation_history.pop(user_id, None)
        await update.message.reply_text(f"Cleared {count} messages from conversation history.")

    async def _handle_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /model [model_string] command."""
        user_id = update.effective_user.id if update.effective_user else 0
        args = context.args or []

        if not args:
            current = _user_models.get(user_id, self.settings.BRAIN_MODEL)
            await update.message.reply_text(
                f"Current model: `{current}`\n\n"
                f"Default brain model: `{self.settings.BRAIN_MODEL}`\n"
                f"Default fast model: `{self.settings.FAST_MODEL}`\n\n"
                f"To change: `/model model-name`",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            new_model = args[0]
            _user_models[user_id] = new_model
            await update.message.reply_text(
                f"Model changed to: `{new_model}`\n"
                f"Use `/model` with no args to reset to default.",
                parse_mode=ParseMode.MARKDOWN,
            )

    async def _handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command - show system info."""
        user_id = update.effective_user.id if update.effective_user else 0
        history_count = len(_conversation_history.get(user_id, []))
        current_model = _user_models.get(user_id, self.settings.BRAIN_MODEL)

        status_text = (
            f"*System Status*\n\n"
            f"Provider: `{self.settings.BRAIN_PROVIDER}`\n"
            f"Brain model: `{current_model}`\n"
            f"Brain mode: `{self.settings.BRAIN_MODE}`\n"
            f"Fast model: `{self.settings.FAST_MODEL}`\n"
            f"Conversation messages: {history_count}\n"
            f"Max iterations: {self.settings.MAX_ITERATIONS}"
        )
        await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)

    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_text = (
            "*Agent Harness Help*\n\n"
            "I'm an AI assistant with access to:\n"
            "• Web search (DuckDuckGo)\n"
            "• Web page fetching\n"
            "• Python code execution\n"
            "• Persistent memory\n"
            "• Sub-agent spawning\n"
            "• Text summarization\n\n"
            "*Commands:*\n"
            "/start - Start fresh\n"
            "/clear - Clear conversation history\n"
            "/model [name] - View or change model\n"
            "/status - Show system status\n"
            "/help - This message\n\n"
            "Just type naturally — I'll use the right tools automatically."
        )
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle incoming user messages.

        Shows typing indicator, runs the orchestrator, sends the response.
        """
        if not update.message or not update.message.text:
            return

        user = update.effective_user
        user_id = user.id if user else 0
        user_text = update.message.text.strip()

        if not user_text:
            return

        logger.info("Message from user %d (%s): %r", user_id, user.username if user else "?", user_text[:80])

        # Show typing indicator
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING,
            )
        except TelegramError:
            pass  # Non-critical

        # Get or initialize conversation history for this user
        history = _conversation_history.setdefault(user_id, [])

        # Optionally use routing to pick the right model
        if self.router:
            try:
                routing = await self.router.route(user_text, history)
                logger.debug("Routing decision: %s", routing)
            except Exception as exc:
                logger.warning("Router failed: %s", exc)

        try:
            result = await self.orchestrator.run(
                user_message=user_text,
                history=history,
            )

            response_text = result.text or "(no response)"

            # Append to history
            history.append(Message(role="user", content=user_text))
            history.append(Message(role="assistant", content=result.text))

            # Trim history if too long
            if len(history) > MAX_HISTORY_MESSAGES:
                history[:] = history[-MAX_HISTORY_MESSAGES:]

            # Send response (split if over Telegram limit)
            await self._send_long_message(update, response_text)

        except Exception as exc:
            logger.error("Orchestrator error for user %d: %s", user_id, exc, exc_info=True)
            error_msg = f"Something went wrong: `{type(exc).__name__}: {exc}`"
            try:
                await update.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)
            except TelegramError:
                await update.message.reply_text(f"Error: {exc}")

    async def _send_long_message(self, update: Update, text: str) -> None:
        """Send a message, splitting into chunks if it exceeds Telegram's limit."""
        if len(text) <= MAX_TELEGRAM_MESSAGE:
            try:
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            except TelegramError:
                # Fallback: send without markdown if formatting causes errors
                await update.message.reply_text(text)
            return

        # Split into chunks at paragraph boundaries where possible
        chunks = _split_message(text, MAX_TELEGRAM_MESSAGE)
        for i, chunk in enumerate(chunks):
            if i > 0:
                # Brief pause between chunks to maintain order
                await asyncio.sleep(0.2)
            try:
                await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
            except TelegramError:
                await update.message.reply_text(chunk)


def _split_message(text: str, max_len: int) -> list[str]:
    """Split text into chunks of at most max_len characters, preferring paragraph breaks."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break

        # Try to split at a paragraph boundary
        split_at = text.rfind("\n\n", 0, max_len)
        if split_at == -1:
            # Try newline
            split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            # Try space
            split_at = text.rfind(" ", 0, max_len)
        if split_at == -1:
            split_at = max_len

        chunks.append(text[:split_at].rstrip())
        text = text[split_at:].lstrip()

    return [c for c in chunks if c]
