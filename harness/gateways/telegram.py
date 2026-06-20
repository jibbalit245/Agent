"""
Telegram gateway — the full bot interface.

Handles:
  - Normal chat messages → agent orchestration
  - /start, /help, /reset  — basic bot commands
  - /agents                 — list available agents
  - /use <name|id>          — switch to an agent
  - /newagent               — conversational wizard to create a new agent
  - /editagent <id> <field> <value>  — update an agent's field
  - /deleteagent <id>       — delete a user-created agent
  - /myagent                — show the currently active agent's config
  - /thinking [level]       — control reasoning depth
  - /workshop [idea]        — start a development pipeline session
"""

import logging
import re
import textwrap
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

from telegram import Update, BotCommand
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)

from harness.agents.agent_config import AgentConfig, ALL_TOOLS, slugify
from harness.agents.agent_manager import AgentManager
from harness.agents.agent_registry import AgentRegistry
from harness.tools.memory_tools import set_session_context

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Wizard conversation states (integers for PTB ConversationHandler)
# ------------------------------------------------------------------

_W_NAME, _W_DESCRIPTION, _W_SYSTEM, _W_MODEL, _W_TOOLS, _W_TEMP, _W_CONFIRM = range(7)

# Workshop states (20-24, non-overlapping with wizard 0-6)
_WS_DISCOVER, _WS_PLAN, _WS_APPROVE, _WS_EXECUTE, _WS_REFINE = range(20, 25)

# ------------------------------------------------------------------
# Workshop coordinator system prompt
# ------------------------------------------------------------------

_WORKSHOP_SYSTEM = """\
You are running a **Workshop Session** — a structured development pipeline to turn raw ideas into executed work.

## Your Phases

### Phase 1: DISCOVER (you are here when context says DISCOVER)
You are a sharp senior architect listening to an idea. Your job:
- Ask *targeted* clarifying questions — one or two at a time, not a list of ten
- Dig into what the person actually wants to BUILD, not just what they said
- Probe: What's the core value? Who uses it? What does success look like in 6 months?
  What's the hardest part? What already exists? What's the budget/timeline?
- After 2-3 rounds, when you have enough, write: "**I think I have enough to plan this. Ready when you are — say 'plan it' or keep going.**"

### Phase 2: PLAN (you are here when context says PLAN)
Generate a concrete, buildable plan. Format exactly:

**UNDERSTANDING**
[What you think they want to build — precise, no filler]

**ASSUMPTIONS**
[Things you're taking as true that could be wrong]

**SCOPE** (this session)
[What we're doing NOW vs what's deferred]

**ARCHITECTURE**
[Key technical decisions with brief rationale]

**IMPLEMENTATION STEPS**
1. [Specific, actionable step with clear deliverable]
2. ...
(Number every step. Be concrete. No vague steps like "set up environment" — say exactly what.)

**AGENT ASSIGNMENTS**
[Which specialized agent (researcher/coder/analyst) handles which steps, if any]

**OPEN QUESTIONS**
[Things that need a decision before we can proceed]

End with: "**Say 'execute' to start, or give me corrections.**"

### Phase 3: EXECUTE (you are here when context says EXECUTE)
You are executing the plan. Use tools aggressively:
- `web_search` + `web_fetch` for current information
- `python_exec` to write, run, and verify code
- `knowledge_search` for platform-specific patterns
- `council_consult` for complex architectural or scientific questions
Show your work. After each major step, output: "✓ Step N complete: [what was done]"

### Phase 4: REFINE (you are here when context says REFINE)
Review what was produced. Identify what's missing, wrong, or incomplete.
Run tests. Fix gaps. Ask: "Is this actually done, or does it just look done?"
When genuinely complete, summarize what was built.

## Rules
- No fluff. Every sentence must carry information.
- If you're unsure what they want, ask — don't guess and build the wrong thing.
- If you hit a genuine blocker, say so clearly: what's blocked, why, what you need.
- Never say "I'll do X" without actually doing it in the same message.
"""

# ------------------------------------------------------------------
# Helper formatting
# ------------------------------------------------------------------

_AVAILABLE_MODELS = [
    "claude-sonnet-4-6",
    "claude-opus-4-5",
    "claude-haiku-4-5-20251001",
    "claude-3-5-sonnet-20241022",
    "claude-3-haiku-20240307",
]

_TOOLS_DESCRIPTION = {
    "web_search":   "Search the web (DuckDuckGo)",
    "web_fetch":    "Fetch and read web pages",
    "python_exec":  "Execute Python code",
    "memory_save":  "Save info to persistent memory",
    "memory_load":  "Load info from persistent memory",
    "summarize":    "Condense long text with AI",
}


def _tools_menu() -> str:
    lines = ["Available tools (send numbers separated by spaces, or 'all'):"]
    for i, name in enumerate(ALL_TOOLS, 1):
        desc = _TOOLS_DESCRIPTION.get(name, "")
        lines.append(f"  {i}. `{name}` — {desc}")
    return "\n".join(lines)


def _parse_tools_input(text: str) -> list[str]:
    """Parse user tool selection: 'all', numbers, or tool names."""
    text = text.strip().lower()
    if text in ("all", "everything", "*"):
        return list(ALL_TOOLS)
    if text in ("none", "nothing", "0", "-"):
        return []
    parts = re.split(r"[\s,]+", text)
    selected = []
    for part in parts:
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(ALL_TOOLS):
                selected.append(ALL_TOOLS[idx])
        elif part in ALL_TOOLS:
            selected.append(part)
    return list(dict.fromkeys(selected))  # preserve order, deduplicate


def _agent_detail(config: AgentConfig) -> str:
    """Format a detailed view of an agent config."""
    tools_str = ", ".join(f"`{t}`" for t in config.tools) or "none"
    prompt_preview = config.system_prompt[:200] + ("..." if len(config.system_prompt) > 200 else "")
    thinking = config.thinking or {}
    if thinking.get("enabled"):
        if "budget_tokens" in thinking:
            thinking_str = f"enabled ({thinking['budget_tokens']} tokens)"
        elif "effort" in thinking:
            thinking_str = f"enabled (effort: {thinking['effort']})"
        else:
            thinking_str = "enabled"
    else:
        thinking_str = "disabled"
    return (
        f"*{config.name}*\n"
        f"ID: `{config.id}`\n"
        f"Description: {config.description or 'N/A'}\n"
        f"Model: `{config.model}`\n"
        f"Mode: `{config.brain_mode}`\n"
        f"Temperature: `{config.temperature}`\n"
        f"Thinking: `{thinking_str}`\n"
        f"Tools: {tools_str}\n"
        f"System prompt preview:\n```\n{prompt_preview}\n```"
    )


# ------------------------------------------------------------------
# Telegram Bot class
# ------------------------------------------------------------------

class TelegramBot:
    """
    Wraps python-telegram-bot to dispatch messages through the AgentManager.
    """

    def __init__(
        self,
        token: str,
        agent_manager: AgentManager,
        agent_registry: AgentRegistry,
        memory_dir: Path = Path("./memory"),
        allowed_user_ids: list[int] | None = None,
    ) -> None:
        self.token = token
        self.manager = agent_manager
        self.registry = agent_registry
        self.memory_dir = memory_dir
        self.allowed_user_ids = set(allowed_user_ids) if allowed_user_ids else None
        self._wizard_data: dict[int, dict[str, Any]] = {}  # user_id → draft config
        self._workshop: dict[int, dict[str, Any]] = {}     # user_id → workshop state

    def _user_id(self, update: Update) -> str:
        """Return a stable string session ID for this Telegram user."""
        return f"telegram_{update.effective_user.id}"

    def _is_allowed(self, update: Update) -> bool:
        if self.allowed_user_ids is None:
            return True
        return update.effective_user.id in self.allowed_user_ids

    async def _setup_session(self, update: Update) -> str:
        """Set memory context and return session ID."""
        uid = self._user_id(update)
        set_session_context(uid, self.memory_dir)
        return uid

    async def _reply(
        self,
        update: Update,
        text: str,
        parse_mode: str = ParseMode.MARKDOWN,
    ) -> None:
        """Send a reply, chunking if over Telegram's 4096 char limit."""
        MAX = 4096
        while text:
            chunk = text[:MAX]
            text = text[MAX:]
            try:
                await update.message.reply_text(chunk, parse_mode=parse_mode)
            except Exception as exc:
                logger.warning("Telegram send failed (%s), retrying plain", exc)
                try:
                    await update.message.reply_text(chunk, parse_mode=None)
                except Exception as exc2:
                    logger.error("Telegram send failed entirely: %s", exc2)

    # ------------------------------------------------------------------
    # Standard commands
    # ------------------------------------------------------------------

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        await self._setup_session(update)
        agents = self.registry.list_agents()
        agent_list = "\n".join(f"  • *{a.name}* (`{a.id}`)" for a in agents[:5])
        text = (
            "*Agent Harness* is ready.\n\n"
            "Just send me a message and I'll respond using the active agent.\n\n"
            f"Available agents:\n{agent_list}\n\n"
            "Commands:\n"
            "  /agents — list all agents\n"
            "  /use `<name>` — switch to an agent\n"
            "  /newagent — create a custom agent\n"
            "  /myagent — show active agent\n"
            "  /reset — clear conversation history\n"
            "  /help — show full help"
        )
        await self._reply(update, text)

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        text = textwrap.dedent("""\
            *Agent Harness — Help*

            *Chat*
            Just send any message to chat with the active agent.

            *Agent Commands*
            /agents — list all available agents
            /use `<name or id>` — switch to a different agent
            /myagent — show the currently active agent's details
            /newagent — start the wizard to create a new agent
            /editagent `<id> <field> <value>` — edit an agent field
            /deleteagent `<id>` — delete a user-created agent

            *Editable fields for /editagent:*
              `name`, `description`, `model`, `system_prompt`,
              `tools`, `temperature`, `brain_mode`

            *Development Pipeline*
            /workshop — start a structured build session (discover → plan → execute → refine)
            /workshop `<idea>` — start with an initial idea
            /wsdone — end current workshop session

            *Reasoning Depth*
            /thinking — show current thinking config
            /thinking off — disable extended reasoning
            /thinking 8000 — enable Claude extended thinking (budget tokens)
            /thinking high — high-effort preset (16k tokens / o-series high effort)
            /thinking low|medium|high — presets

            *Conversation*
            /reset — clear chat history with current agent

            *Examples*
            `/use researcher`
            `/editagent my-bot temperature 0.9`
            `/editagent my-bot tools web_search,python_exec`
        """)
        await self._reply(update, text)

    async def cmd_reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        uid = await self._setup_session(update)
        self.manager.clear_history(uid)
        await self._reply(update, "Conversation history cleared.")

    # ------------------------------------------------------------------
    # Agent list & switch
    # ------------------------------------------------------------------

    async def cmd_agents(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        uid = await self._setup_session(update)
        agents = self.registry.list_agents()
        if not agents:
            await self._reply(update, "No agents configured. Use /newagent to create one.")
            return

        active_id = self.manager.get_active_agent_id(uid)
        lines = ["*Available Agents:*\n"]
        for a in agents:
            active_marker = " <- active" if a.id == active_id else ""
            lines.append(f"• *{a.name}* (`{a.id}`){active_marker}")
            if a.description:
                lines.append(f"  _{a.description}_")

        lines.append("\nUse `/use <name>` to switch agents.")
        await self._reply(update, "\n".join(lines))

    async def cmd_use(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        uid = await self._setup_session(update)

        if not context.args:
            await self._reply(update, "Usage: `/use <agent name or id>`")
            return

        query = " ".join(context.args)
        config = self.registry.find(query)
        if config is None:
            agents = self.registry.list_agents()
            names = ", ".join(f"`{a.id}`" for a in agents)
            await self._reply(update, f"Agent not found: `{query}`\n\nAvailable: {names}")
            return

        try:
            self.manager.use_agent(uid, config.id)
            await self._reply(
                update,
                f"Switched to *{config.name}*.\n_{config.description or ''}_\n\n"
                f"Model: `{config.model}` | Tools: {len(config.tools)}\n\n"
                "Start chatting — history has been reset for this switch."
            )
        except Exception as exc:
            logger.error("cmd_use failed: %s", exc)
            await self._reply(update, f"Failed to switch agent: {exc}")

    async def cmd_myagent(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        uid = await self._setup_session(update)
        session = self.manager.get_active_session(uid)
        if session is None:
            await self._reply(update, "No active agent. Use /agents to see options.")
            return
        await self._reply(update, _agent_detail(session.agent_config))

    # ------------------------------------------------------------------
    # Edit agent
    # ------------------------------------------------------------------

    async def cmd_editagent(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        await self._setup_session(update)

        if not context.args or len(context.args) < 3:
            await self._reply(
                update,
                "Usage: `/editagent <id> <field> <value>`\n\n"
                "Editable fields: `name`, `description`, `model`, `system_prompt`, "
                "`tools`, `temperature`, `brain_mode`"
            )
            return

        agent_id = context.args[0]
        field = context.args[1].lower()
        value = " ".join(context.args[2:])

        config = self.registry.get(agent_id)
        if config is None:
            await self._reply(update, f"Agent not found: `{agent_id}`")
            return

        editable_fields = {
            "name", "description", "model", "system_prompt",
            "tools", "temperature", "brain_mode",
        }
        if field not in editable_fields:
            await self._reply(
                update,
                f"Unknown field: `{field}`\n\nEditable fields: {', '.join(sorted(editable_fields))}"
            )
            return

        try:
            if field == "temperature":
                setattr(config, field, float(value))
            elif field == "tools":
                tool_names = [t.strip() for t in re.split(r"[,\s]+", value) if t.strip()]
                valid = [t for t in tool_names if t in ALL_TOOLS]
                invalid = [t for t in tool_names if t not in ALL_TOOLS]
                if invalid:
                    await self._reply(update, f"Unknown tools (ignored): {', '.join(invalid)}")
                config.tools = valid
            elif field == "name":
                config.name = value
                new_id = slugify(value)
                if new_id != config.id and not self.registry.exists(new_id):
                    config.id = new_id
            else:
                setattr(config, field, value)

            config.touch()
            self.registry.save(config)
            await self._reply(
                update,
                f"Updated `{field}` on *{config.name}*.\n\n{_agent_detail(config)}"
            )
        except ValueError as exc:
            await self._reply(update, f"Invalid value: {exc}")
        except Exception as exc:
            logger.error("cmd_editagent failed: %s", exc)
            await self._reply(update, f"Failed to update agent: {exc}")

    # ------------------------------------------------------------------
    # Delete agent
    # ------------------------------------------------------------------

    async def cmd_deleteagent(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        uid = await self._setup_session(update)

        if not context.args:
            await self._reply(update, "Usage: `/deleteagent <id>`")
            return

        agent_id = context.args[0]
        config = self.registry.get(agent_id)
        if config is None:
            await self._reply(update, f"Agent not found: `{agent_id}`")
            return

        deleted = self.registry.delete(agent_id)
        if deleted:
            active_session = self.manager.get_active_session(uid)
            if active_session and active_session.agent_config.id == agent_id:
                self.manager.clear_history(uid)
            await self._reply(update, f"Deleted agent: *{config.name}* (`{agent_id}`)")
        else:
            await self._reply(
                update,
                f"Cannot delete `{agent_id}` — it may be a built-in default agent.\n"
                "Built-in agents (researcher, coder, analyst) cannot be deleted."
            )

    # ------------------------------------------------------------------
    # New agent wizard (ConversationHandler states)
    # ------------------------------------------------------------------

    async def wizard_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Entry point for /newagent wizard."""
        if not self._is_allowed(update):
            return ConversationHandler.END
        user_id = update.effective_user.id
        self._wizard_data[user_id] = {}
        await self._reply(
            update,
            "*Create a New Agent*\n\nStep 1/6: What should this agent be called?\n\n"
            "Enter a name (e.g. `ResearchBot`, `My Coder`, `DataAnalyst`):"
        )
        return _W_NAME

    async def wizard_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        name = update.message.text.strip()
        if not name or len(name) < 2:
            await self._reply(update, "Name must be at least 2 characters. Try again:")
            return _W_NAME
        self._wizard_data[user_id]["name"] = name
        agent_id = slugify(name)
        await self._reply(
            update,
            f"Name: *{name}* (ID: `{agent_id}`)\n\n"
            "Step 2/6: Add a short description (optional).\n\n"
            "What does this agent specialise in? (or send `-` to skip):"
        )
        return _W_DESCRIPTION

    async def wizard_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        text = update.message.text.strip()
        self._wizard_data[user_id]["description"] = "" if text == "-" else text
        await self._reply(
            update,
            "Step 3/6: *System Prompt / Persona*\n\n"
            "Write the system prompt that defines this agent's personality and expertise. "
            "This is shown to the model at the start of every conversation.\n\n"
            "Example:\n"
            "```\n"
            "You are a friendly cooking assistant who specialises in Italian cuisine. "
            "Always suggest substitutions for common allergens.\n"
            "```\n\n"
            "Write your system prompt now (or send `-` for default):"
        )
        return _W_SYSTEM

    async def wizard_system_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        text = update.message.text.strip()
        if text == "-":
            text = "You are a helpful AI assistant."
        self._wizard_data[user_id]["system_prompt"] = text

        models_list = "\n".join(f"  {i}. `{m}`" for i, m in enumerate(_AVAILABLE_MODELS, 1))
        await self._reply(
            update,
            f"Step 4/6: *Choose a Model*\n\n{models_list}\n\n"
            "Send the number or the model ID (default: `claude-sonnet-4-6`):"
        )
        return _W_MODEL

    async def wizard_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        text = update.message.text.strip()

        if text.isdigit():
            idx = int(text) - 1
            if 0 <= idx < len(_AVAILABLE_MODELS):
                model = _AVAILABLE_MODELS[idx]
            else:
                model = "claude-sonnet-4-6"
        elif text in _AVAILABLE_MODELS:
            model = text
        elif text in ("-", ""):
            model = "claude-sonnet-4-6"
        else:
            model = text  # Accept any custom model string

        self._wizard_data[user_id]["model"] = model
        await self._reply(
            update,
            f"Model: `{model}`\n\n"
            f"Step 5/6: *Select Tools*\n\n{_tools_menu()}\n\n"
            "Send numbers separated by spaces, tool names, `all`, or `none`:"
        )
        return _W_TOOLS

    async def wizard_tools(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        text = update.message.text.strip()
        tools = _parse_tools_input(text)
        if text and not tools and text.lower() not in ("none", "nothing", "-"):
            await self._reply(
                update,
                f"Could not parse tool selection: `{text}`\n\n"
                f"Send numbers (1-{len(ALL_TOOLS)}), tool names, `all`, or `none`:"
            )
            return _W_TOOLS

        self._wizard_data[user_id]["tools"] = tools
        tools_str = ", ".join(f"`{t}`" for t in tools) if tools else "none"
        await self._reply(
            update,
            f"Tools: {tools_str}\n\n"
            "Step 6/6: *Temperature*\n\n"
            "Controls creativity vs precision:\n"
            "  `0.0`-`0.3` — precise, deterministic\n"
            "  `0.5`-`0.7` — balanced (default)\n"
            "  `0.8`-`1.0` — creative, varied\n\n"
            "Send a value between 0.0 and 1.0 (or `-` for default 0.7):"
        )
        return _W_TEMP

    async def wizard_temperature(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        text = update.message.text.strip()

        temp = 0.7
        if text != "-":
            try:
                temp = float(text)
                if not (0.0 <= temp <= 1.0):
                    await self._reply(update, "Temperature must be between 0.0 and 1.0. Try again:")
                    return _W_TEMP
            except ValueError:
                await self._reply(update, "Please send a number like `0.7`. Try again:")
                return _W_TEMP

        self._wizard_data[user_id]["temperature"] = temp

        draft = self._wizard_data[user_id]
        name = draft["name"]
        desc = draft.get("description", "") or "N/A"
        model = draft["model"]
        tools = draft["tools"]
        system_preview = draft["system_prompt"][:150] + ("..." if len(draft["system_prompt"]) > 150 else "")
        tools_str = ", ".join(f"`{t}`" for t in tools) if tools else "none"

        summary = (
            f"*Summary — confirm creation?*\n\n"
            f"*Name:* {name}\n"
            f"*Description:* {desc}\n"
            f"*Model:* `{model}`\n"
            f"*Temperature:* `{temp}`\n"
            f"*Tools:* {tools_str}\n"
            f"*System prompt:*\n```\n{system_preview}\n```\n\n"
            "Send `yes` to create, `no` to cancel, or `edit` to restart:"
        )
        await self._reply(update, summary)
        return _W_CONFIRM

    async def wizard_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        text = update.message.text.strip().lower()

        if text in ("no", "cancel", "n"):
            self._wizard_data.pop(user_id, None)
            await self._reply(update, "Agent creation cancelled.")
            return ConversationHandler.END

        if text in ("edit", "restart", "redo"):
            self._wizard_data.pop(user_id, None)
            await self._reply(update, "Restarting wizard. Use /newagent to begin again.")
            return ConversationHandler.END

        if text not in ("yes", "y", "create", "ok", "confirm"):
            await self._reply(update, "Please send `yes` to confirm or `no` to cancel.")
            return _W_CONFIRM

        draft = self._wizard_data.pop(user_id, {})
        if not draft:
            await self._reply(update, "Session expired. Please run /newagent again.")
            return ConversationHandler.END

        try:
            config = AgentConfig.create(
                name=draft["name"],
                description=draft.get("description", ""),
                model=draft["model"],
                system_prompt=draft["system_prompt"],
                tools=draft["tools"],
                temperature=draft["temperature"],
            )

            # Ensure unique ID
            if self.registry.exists(config.id):
                config.id = config.id + "-custom"

            self.registry.save(config)

            await self._reply(
                update,
                f"*Agent created!*\n\n{_agent_detail(config)}\n\n"
                f"Use `/use {config.id}` to start chatting with it."
            )
        except Exception as exc:
            logger.error("wizard_confirm failed: %s", exc)
            await self._reply(update, f"Failed to create agent: {exc}")

        return ConversationHandler.END

    async def wizard_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        self._wizard_data.pop(user_id, None)
        await self._reply(update, "Agent creation cancelled. Use /newagent to start again.")
        return ConversationHandler.END

    # ------------------------------------------------------------------
    # Thinking control
    # ------------------------------------------------------------------

    async def cmd_thinking(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        /thinking            — show current thinking config
        /thinking off        — disable extended thinking
        /thinking <N>        — enable with Claude budget_tokens=N (e.g. /thinking 8000)
        /thinking low|medium|high  — preset budgets (2000 / 6000 / 16000) or o-series effort
        /thinking effort <level>   — explicitly set o-series effort (low/medium/high)
        """
        if not self._is_allowed(update):
            return
        uid = await self._setup_session(update)
        session = self.manager.get_active_session(uid)

        if not context.args:
            current = self.manager.get_thinking(uid) or {}
            if not current or not current.get("enabled"):
                await self._reply(update, (
                    "*Thinking: disabled*\n\n"
                    "Extended reasoning is off. Commands:\n"
                    "  `/thinking off` — keep disabled\n"
                    "  `/thinking <N>` — enable with N budget tokens (e.g. `/thinking 8000`)\n"
                    "  `/thinking low|medium|high` — preset budgets\n"
                    "  `/thinking effort high` — set o-series reasoning effort"
                ))
            else:
                budget = current.get("budget_tokens")
                effort = current.get("effort")
                detail = f"budget_tokens: `{budget}`" if budget else f"effort: `{effort}`"
                await self._reply(update, (
                    f"*Thinking: enabled*\n{detail}\n\n"
                    "Commands:\n"
                    "  `/thinking off` — disable\n"
                    "  `/thinking <N>` — change budget (e.g. `/thinking 12000`)\n"
                    "  `/thinking low|medium|high` — presets\n"
                    "  `/thinking effort high` — o-series effort"
                ))
            return

        arg = context.args[0].lower()

        _PRESETS = {
            "low":    {"enabled": True, "budget_tokens": 2000, "effort": "low"},
            "medium": {"enabled": True, "budget_tokens": 6000, "effort": "medium"},
            "high":   {"enabled": True, "budget_tokens": 16000, "effort": "high"},
            "max":    {"enabled": True, "budget_tokens": 32000, "effort": "high"},
        }

        if arg in ("off", "disable", "false", "no", "0"):
            new_thinking = {"enabled": False}
            label = "disabled"

        elif arg in _PRESETS:
            new_thinking = _PRESETS[arg]
            label = f"enabled — {arg} preset"

        elif arg == "effort" and len(context.args) >= 2:
            level = context.args[1].lower()
            if level not in ("low", "medium", "high"):
                await self._reply(update, "Effort must be `low`, `medium`, or `high`.")
                return
            new_thinking = {"enabled": True, "effort": level}
            label = f"enabled — effort `{level}`"

        elif arg.isdigit() or (arg.replace(".", "", 1).isdigit()):
            budget = int(float(arg))
            if budget < 100:
                await self._reply(update, "Budget must be at least 100 tokens.")
                return
            if budget > 32000:
                await self._reply(update, "Maximum budget is 32000 tokens (Claude limit).")
                return
            new_thinking = {"enabled": True, "budget_tokens": budget}
            label = f"enabled — `{budget}` budget tokens"

        else:
            await self._reply(update, (
                "Unknown thinking command.\n\n"
                "Usage:\n"
                "  `/thinking` — show current\n"
                "  `/thinking off` — disable\n"
                "  `/thinking 8000` — enable with 8000 budget tokens\n"
                "  `/thinking low|medium|high` — preset\n"
                "  `/thinking effort high` — o-series effort"
            ))
            return

        updated = self.manager.set_thinking(uid, new_thinking)
        if updated:
            await self._reply(update, f"Thinking {label}. Takes effect on your next message.")
        else:
            await self._reply(update, "No active session. Send a message first to start one.")

    # ------------------------------------------------------------------
    # Main message handler
    # ------------------------------------------------------------------

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle a regular chat message — route through the agent manager."""
        if not self._is_allowed(update):
            return
        uid = await self._setup_session(update)

        user_text = update.message.text or ""
        if not user_text.strip():
            return

        await update.message.chat.send_action("typing")

        try:
            result = await self.manager.chat(uid, user_text)
            response_text = result.text or "(no response)"
            await self._reply(update, response_text)

            if result.tool_calls_made:
                logger.info(
                    "User %s: %d tool call(s) in %d iteration(s)",
                    uid, len(result.tool_calls_made), result.iterations,
                )
        except Exception as exc:
            logger.error("handle_message failed for %s: %s", uid, exc, exc_info=True)
            await self._reply(
                update,
                f"Something went wrong: {type(exc).__name__}: {exc}\n\n"
                "Try /reset to clear history if this persists.",
                parse_mode=None,
            )

    # ------------------------------------------------------------------
    # Workshop pipeline
    # ------------------------------------------------------------------

    def _ws_session_id(self, user_id: int) -> str:
        return f"workshop_{user_id}"

    async def _ws_chat(self, user_id: int, phase: str, message: str) -> str:
        """Route a workshop message through the orchestrator with phase context injected."""
        from harness.core.orchestrator import Orchestrator
        from harness.core.brain import Brain
        from harness.tools.registry import registry as tool_registry

        ws = self._workshop[user_id]

        # Build or reuse the workshop orchestrator (uses primary provider/model)
        if "orchestrator" not in ws:
            session = self.manager.ensure_session(f"telegram_{user_id}")
            provider_name = session.agent_config.provider
            provider = self.manager.providers.get(provider_name) or next(
                iter(self.manager.providers.values())
            )
            brain = Brain(
                provider=provider,
                model=session.agent_config.model,
                mode=session.agent_config.brain_mode,
                system_prompt=_WORKSHOP_SYSTEM,
                thinking=session.agent_config.thinking or None,
            )
            ws["orchestrator"] = Orchestrator(
                brain=brain,
                tool_registry=tool_registry,
                max_iterations=15,
                system_prompt=_WORKSHOP_SYSTEM,
            )
            ws["history"] = []

        # Inject phase context
        prefixed = f"[WORKSHOP PHASE: {phase}]\n\n{message}"

        result = await ws["orchestrator"].run(
            user_message=prefixed,
            history=ws["history"],
            temperature=0.4,
            max_tokens=4096,
        )

        from harness.providers.base import Message
        ws["history"].append(Message(role="user", content=prefixed))
        ws["history"].append(Message(role="assistant", content=result.text))

        return result.text or "(no response)"

    async def ws_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Entry point: /workshop [optional initial idea]"""
        if not self._is_allowed(update):
            return ConversationHandler.END
        uid = update.effective_user.id
        await self._setup_session(update)

        self._workshop[uid] = {"phase": "DISCOVER"}

        initial = " ".join(context.args) if context.args else ""

        await self._reply(
            update,
            "*Workshop Session Started* 🔨\n\n"
            "This is a structured development pipeline:\n"
            "  1. *Discover* — we nail down what you're building\n"
            "  2. *Plan* — concrete implementation steps\n"
            "  3. *Execute* — I build it with full tool access\n"
            "  4. *Refine* — fill gaps, polish, complete\n\n"
            "Commands during the session:\n"
            "  `plan it` / `let's plan` → jump to planning\n"
            "  `execute` → start execution\n"
            "  `refine` → switch to refinement\n"
            "  `/wsdone` → end session\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "**What are you building?** Tell me everything — don't filter yourself."
            + (f"\n\n_(You said: {initial})_" if initial else ""),
        )

        if initial:
            response = await self._ws_chat(uid, "DISCOVER", initial)
            await self._reply(update, response)

        return _WS_DISCOVER

    async def ws_discover(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """DISCOVER phase — free-form idea exploration."""
        uid = update.effective_user.id
        text = update.message.text.strip()

        # Check for phase transition keywords
        lower = text.lower()
        if any(k in lower for k in ("plan it", "let's plan", "lets plan", "make a plan", "ready to plan")):
            return await self._transition_to_plan(update, uid, text)

        await update.message.chat.send_action("typing")
        response = await self._ws_chat(uid, "DISCOVER", text)
        await self._reply(update, response)

        # Auto-detect if AI is signaling readiness to plan
        if "ready when you are" in response.lower() or "say 'plan it'" in response.lower():
            self._workshop[uid]["ai_ready"] = True

        return _WS_DISCOVER

    async def _transition_to_plan(self, update: Update, uid: int, trigger_text: str) -> int:
        """Transition from DISCOVER to PLAN phase."""
        self._workshop[uid]["phase"] = "PLAN"
        await update.message.chat.send_action("typing")
        response = await self._ws_chat(uid, "PLAN", trigger_text)
        await self._reply(update, response)
        return _WS_PLAN

    async def ws_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """PLAN phase — user reviews and adjusts the plan."""
        uid = update.effective_user.id
        text = update.message.text.strip()
        lower = text.lower()

        if any(k in lower for k in ("execute", "start", "go", "do it", "let's go", "build it")):
            self._workshop[uid]["phase"] = "EXECUTE"
            await update.message.chat.send_action("typing")
            intro = await self._ws_chat(uid, "EXECUTE", "Begin executing the plan. Start with step 1.")
            await self._reply(update, intro)
            return _WS_EXECUTE

        await update.message.chat.send_action("typing")
        response = await self._ws_chat(uid, "PLAN", text)
        await self._reply(update, response)
        return _WS_PLAN

    async def ws_execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """EXECUTE phase — AI does the work with full tool access."""
        uid = update.effective_user.id
        text = update.message.text.strip()
        lower = text.lower()

        if any(k in lower for k in ("refine", "review", "done", "next step", "what's next")):
            self._workshop[uid]["phase"] = "REFINE"
            await update.message.chat.send_action("typing")
            response = await self._ws_chat(uid, "REFINE", text)
            await self._reply(update, response)
            return _WS_REFINE

        await update.message.chat.send_action("typing")
        response = await self._ws_chat(uid, "EXECUTE", text)
        await self._reply(update, response)
        return _WS_EXECUTE

    async def ws_refine(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """REFINE phase — review, fill gaps, iterate."""
        uid = update.effective_user.id
        text = update.message.text.strip()
        lower = text.lower()

        if any(k in lower for k in ("execute more", "keep going", "continue", "do more")):
            self._workshop[uid]["phase"] = "EXECUTE"
            await update.message.chat.send_action("typing")
            response = await self._ws_chat(uid, "EXECUTE", text)
            await self._reply(update, response)
            return _WS_EXECUTE

        await update.message.chat.send_action("typing")
        response = await self._ws_chat(uid, "REFINE", text)
        await self._reply(update, response)
        return _WS_REFINE

    async def ws_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """End the workshop session."""
        uid = update.effective_user.id
        ws = self._workshop.pop(uid, {})
        turns = len(ws.get("history", [])) // 2
        await self._reply(
            update,
            f"*Workshop session ended.* ({turns} turns)\n\n"
            "Your normal chat session is still active. Start a new one with `/workshop`."
        )
        return ConversationHandler.END

    async def ws_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        uid = update.effective_user.id
        self._workshop.pop(uid, None)
        await self._reply(update, "Workshop cancelled. Use `/workshop` to start a new one.")
        return ConversationHandler.END

    # ------------------------------------------------------------------
    # Application builder
    # ------------------------------------------------------------------

    def build_application(self) -> Application:
        """Build and return the configured PTB Application."""
        app = Application.builder().token(self.token).build()

        # Newagent wizard ConversationHandler
        wizard = ConversationHandler(
            entry_points=[CommandHandler("newagent", self.wizard_start)],
            states={
                _W_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.wizard_name)],
                _W_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.wizard_description)],
                _W_SYSTEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.wizard_system_prompt)],
                _W_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.wizard_model)],
                _W_TOOLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.wizard_tools)],
                _W_TEMP: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.wizard_temperature)],
                _W_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.wizard_confirm)],
            },
            fallbacks=[CommandHandler("cancel", self.wizard_cancel)],
            allow_reentry=True,
        )

        # Workshop ConversationHandler
        _ws_text = filters.TEXT & ~filters.COMMAND
        workshop = ConversationHandler(
            entry_points=[CommandHandler("workshop", self.ws_start)],
            states={
                _WS_DISCOVER: [
                    CommandHandler("wsdone", self.ws_done),
                    MessageHandler(_ws_text, self.ws_discover),
                ],
                _WS_PLAN: [
                    CommandHandler("wsdone", self.ws_done),
                    MessageHandler(_ws_text, self.ws_plan),
                ],
                _WS_EXECUTE: [
                    CommandHandler("wsdone", self.ws_done),
                    MessageHandler(_ws_text, self.ws_execute),
                ],
                _WS_REFINE: [
                    CommandHandler("wsdone", self.ws_done),
                    MessageHandler(_ws_text, self.ws_refine),
                ],
            },
            fallbacks=[
                CommandHandler("cancel", self.ws_cancel),
                CommandHandler("wsdone", self.ws_done),
            ],
            allow_reentry=True,
        )

        app.add_handler(workshop)
        app.add_handler(wizard)
        app.add_handler(CommandHandler("start", self.cmd_start))
        app.add_handler(CommandHandler("help", self.cmd_help))
        app.add_handler(CommandHandler("reset", self.cmd_reset))
        app.add_handler(CommandHandler("agents", self.cmd_agents))
        app.add_handler(CommandHandler("use", self.cmd_use))
        app.add_handler(CommandHandler("myagent", self.cmd_myagent))
        app.add_handler(CommandHandler("editagent", self.cmd_editagent))
        app.add_handler(CommandHandler("deleteagent", self.cmd_deleteagent))
        app.add_handler(CommandHandler("thinking", self.cmd_thinking))
        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        return app

    async def setup_commands(self, app: Application) -> None:
        """Register bot commands with Telegram (shows in the menu)."""
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help"),
            BotCommand("agents", "List available agents"),
            BotCommand("use", "Switch to an agent: /use <name>"),
            BotCommand("myagent", "Show active agent details"),
            BotCommand("newagent", "Create a new custom agent"),
            BotCommand("editagent", "Edit an agent: /editagent <id> <field> <value>"),
            BotCommand("deleteagent", "Delete an agent: /deleteagent <id>"),
            BotCommand("thinking", "Control reasoning depth: /thinking [off|low|medium|high|N]"),
            BotCommand("workshop", "Start development pipeline: /workshop [initial idea]"),
            BotCommand("wsdone", "End the current workshop session"),
            BotCommand("reset", "Clear conversation history"),
            BotCommand("cancel", "Cancel current operation"),
        ]
        await app.bot.set_my_commands(commands)

    def run(self) -> None:
        """Build the application and run the polling loop (blocking)."""
        app = self.build_application()
        logger.info("Starting Telegram bot polling...")

        async def post_init(application: Application) -> None:
            await self.setup_commands(application)

        app.post_init = post_init
        app.run_polling(drop_pending_updates=True)
