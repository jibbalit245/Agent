# Claude Code
> Source: https://docs.anthropic.com/en/docs/claude-code/overview
> Fetched: 2026-06-20

## What is Claude Code?

Claude Code is Anthropic's AI coding agent that runs in your terminal. It can:
- Read and write files in your repository
- Run shell commands and tests
- Browse the web and fetch URLs
- Call external APIs and MCP tools
- Manage git operations (commit, PR creation, branch management)
- Operate autonomously on multi-step coding tasks

## Installation

### npm (universal)
```bash
npm install -g @anthropic-ai/claude-code
```

### Native binary installer
A native binary installer is also available — no Node.js or npm required. Also available via Homebrew (macOS), WinGet (Windows), and PowerShell installer.

### Verify install
```bash
claude --version
claude  # start a session
```

## Authentication

```bash
# Set API key before launching
export ANTHROPIC_API_KEY="sk-ant-api03-..."
claude

# Or log in via browser (prompts on first launch)
claude  # opens browser for OAuth login
```

## CLAUDE.md — Project Context File

`CLAUDE.md` is read by Claude at session start. Place it in the project root or `~/.claude/CLAUDE.md` for global instructions.

Think of it as: **settings = what Claude can do; CLAUDE.md = what Claude should know**.

```markdown
# Project: MyApp

## Tech Stack
- Python 3.12, FastAPI, PostgreSQL
- Tests: pytest, run with `pytest tests/`

## Conventions
- Use snake_case for variables
- All functions must have type hints
- Commit format: `type(scope): message`

## Common Commands
- `make test` — run test suite
- `make lint` — run ruff + mypy
```

CLAUDE.md files are hierarchical:
- `~/.claude/CLAUDE.md` — global user instructions
- `.claude/CLAUDE.md` or `CLAUDE.md` — project instructions (committed to repo)

## settings.json — Configuration

### File Locations (in priority order)

| File | Scope |
|------|-------|
| `~/.claude/settings.json` | Global user baseline |
| `.claude/settings.json` | Project team settings (committed) |
| `.claude/settings.local.json` | Personal project overrides (gitignored) |

### Example settings.json

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(git *)",
      "Read(**)",
      "Write(src/**)"
    ],
    "deny": [
      "Bash(rm -rf *)"
    ]
  },
  "env": {
    "NODE_ENV": "development"
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Running bash command'"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "npm run build 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### Key settings.json Categories (v2.1.104+, ~125+ keys)

| Category | Key examples |
|----------|-------------|
| **Permissions** | `permissions.allow`, `permissions.deny` — tool allowlists/denylists |
| **Hooks** | `hooks.PreToolUse`, `hooks.PostToolUse`, `hooks.SessionStart`, `hooks.SessionEnd`, `hooks.UserPromptSubmit`, `hooks.Notification`, `hooks.PreCompact` |
| **Model** | Model selection, effort levels (fast/balanced/thorough), extended thinking |
| **MCP** | MCP server allowlists/blocklists |
| **Environment** | `env` — key/value pairs injected into the session |
| **Security** | Filesystem read/write allowlists and denylists, process sandboxing |
| **Memory** | Auto-memory extraction, background consolidation, transcript retention |
| **UI** | Theme, status line, spinner, output styling |

## Hooks

Hooks are shell commands executed at lifecycle events. They can block tool calls, log events, or trigger automation.

### Hook Events

| Event | When it fires |
|-------|--------------|
| `PreToolUse` | Before any tool call — can block it |
| `PostToolUse` | After a tool call completes |
| `UserPromptSubmit` | When user submits a prompt |
| `Notification` | When Claude sends a notification |
| `SessionStart` | When a session begins |
| `SessionEnd` | When a session ends |
| `PreCompact` | Before context compaction |

### Hook Example

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --check $CLAUDE_TOOL_INPUT_FILE_PATH 2>&1"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/my-logger.sh"
          }
        ]
      }
    ]
  }
}
```

Hooks can return non-zero exit codes to block tool execution.

## MCP Servers (Model Context Protocol)

MCP extends Claude with additional tools. Configuration lives in separate files:

| File | Scope |
|------|-------|
| `~/.claude.json` | Global user MCP servers |
| `.mcp.json` | Project-level MCP servers |

### MCP Config Example (.mcp.json)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    }
  }
}
```

### Add MCP server via CLI

```bash
claude mcp add my-server -e API_KEY=xxx -- /path/to/server
claude mcp list
claude mcp remove my-server
```

## Slash Commands

Run these inside a Claude Code session:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/clear` | Reset conversation (empty context) |
| `/compact` | Summarize older messages to reduce context |
| `/model` | Switch the active model |
| `/permissions` | View/modify allowed tools |
| `/cost` | Show token usage and cost for session |
| `/review` | Trigger a code review skill |
| `/config` | Open configuration settings |

Use `/help` to see all commands available in your version — the list varies by version and installed plugins.

## Skills

Skills are reusable prompt workflows stored as `.md` files:

```
.claude/skills/
  deploy.md
  test-coverage.md
```

Invoke with `/deploy` or `/test-coverage` in a session.

## Subagents / Agents

Claude Code can spawn specialized subagents for isolated tasks:

```
.claude/agents/
  code-reviewer.md
  security-auditor.md
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Primary API key for authentication |
| `ANTHROPIC_AUTH_TOKEN` | Alternative auth (do not set both) |
| `ANTHROPIC_BASE_URL` | Override API base URL (e.g., for proxies) |
| `CLAUDE_CODE_MAX_TOKENS` | Override default max tokens |
| `CLAUDE_CODE_DISABLE_TELEMETRY` | Disable usage telemetry |

## Keybindings

Default shortcuts (customizable in `~/.claude/keybindings.json`):

| Action | Default |
|--------|---------|
| Submit prompt | Enter |
| New line | Shift+Enter |
| Cancel generation | Escape |
| History up/down | Arrow keys |

## Common Workflows

```bash
# Start a session in current project
claude

# Run a one-shot command (non-interactive)
claude -p "Fix the failing tests in tests/test_auth.py"

# Run with a specific model
claude --model claude-opus-4-8

# Print output without interactive session
claude -p "What does this function do?" --no-interactive
```

## File Structure Summary

```
project/
  CLAUDE.md              # Project instructions
  .claude/
    settings.json        # Team settings (commit this)
    settings.local.json  # Personal overrides (gitignore)
    agents/              # Custom subagent definitions
    skills/              # Reusable prompt workflows
  .mcp.json              # MCP server config (project-level)

~/.claude/
  settings.json          # Global user settings
  CLAUDE.md              # Global user instructions
  keybindings.json       # Custom keybindings
~/.claude.json           # Global MCP server config
```
