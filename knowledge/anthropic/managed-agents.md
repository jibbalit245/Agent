# Managed Agents
> Source: https://platform.claude.com/docs/en/managed-agents/overview.md
> Fetched: 2026-06-20
---

## Overview

Managed Agents provisions a container per session as the agent's workspace. The agent loop runs on Anthropic's orchestration layer; the container is where the agent's tools execute — bash commands, file operations, code.

**Architecture:**
- **Agent** — A persisted, versioned config: model, system prompt, tools, MCP servers, skills. **Must be created before starting a session.**
- **Session** — A stateful interaction with an agent. References a pre-created agent by ID + an environment + initial instructions. Produces an event stream.
- **Environment** — A template defining the configuration for container provisioning.
- **Container** — An isolated compute instance where the agent's tools execute.

## The Mandatory Flow: Agent (Once) → Session (Every Run)

```
Agent (config) ──▶ Anthropic orchestration layer ──▶ Container (tool execution)
                         (agent loop: Claude + tool calls)
                                   │
                         Session ──┤
                                   ├── Resources (files, repos, memory stores)
                                   ├── Vault IDs (MCP credential references)
                                   └── Conversation (event stream in/out)
```

| Step | Call | Frequency |
|---|---|---|
| 1 | `POST /v1/agents` | **ONCE.** Store `agent.id` and `agent.version`. |
| 2 | `POST /v1/sessions` | **Every run.** String shorthand uses latest version. |

**Anti-pattern:** calling `agents.create()` at the top of every script run. This accumulates orphaned agent objects.

## Beta Headers

| Beta Header | What it enables |
| --- | --- |
| `managed-agents-2026-04-01` | Agents, Environments, Sessions, Events, Outcomes, Multiagent, Vaults, Memory Stores, Deployments |
| `skills-2025-10-02` | Skills API |
| `files-api-2025-04-14` | Files API |

## Creating an Agent (Python)

```python
import anthropic

client = anthropic.Anthropic()

# Create the agent ONCE and store the ID
agent = client.beta.agents.create(
    name="Coding Assistant",
    model="claude-opus-4-8",
    system="You are a helpful coding agent.",
    tools=[{"type": "agent_toolset_20260401"}],
)

# Store agent.id in config/env — reuse it
agent_id = agent.id
agent_version = agent.version
```

## Creating a Session

```python
environment = client.beta.environments.create(
    name="Default Environment",
)

session = client.beta.sessions.create(
    agent=agent_id,  # string shorthand → latest version
    # or: {"type": "agent", "id": agent_id, "version": agent_version}
    environment_id=environment.id,
    title="My Task",
)
```

**Session creation parameters:**

| Field | Required | Description |
| --- | --- | --- |
| `agent` | Yes | String agent ID (latest) or `{type, id, version}` |
| `environment_id` | Yes | Environment ID |
| `title` | No | Human-readable name |
| `resources` | No | Files, GitHub repos, or memory stores |
| `vault_ids` | No | Vault IDs for MCP credentials |
| `metadata` | No | User-provided key-value pairs |

## Agent Configuration (passed to `agents.create()`)

| Field | Required | Description |
| --- | --- | --- |
| `name` | Yes | Human-readable name (1-256 chars) |
| `model` | Yes | Claude model ID (Claude 4.5+ supported) |
| `system` | No | System prompt (up to 100K chars) |
| `tools` | No | Agent toolset / MCP toolset / custom tools (max 128) |
| `mcp_servers` | No | MCP server connections (max 20) |
| `skills` | No | Skill references (max 20) |
| `description` | No | Description of the agent (up to 2048 chars) |
| `multiagent` | No | `{type: "coordinator", agents: [...]}` |
| `metadata` | No | Arbitrary key-value pairs |

## Session Lifecycle

```
rescheduling → running ↔ idle → terminated
```

| Status | Description |
| --- | --- |
| `idle` | Agent finished current task, awaiting input |
| `running` | Session has started running, agent is actively doing work |
| `rescheduling` | Session is rescheduling after a retryable error |
| `terminated` | Session has terminated, irreversible |

**Built-in session features:**
- Context compaction — if you approach max context, the API automatically condenses session history
- Prompt caching — historical repeated tokens are cached
- Extended thinking — on by default, returned as `agent.thinking` events

## Sending Events to a Session

```python
session_event = client.beta.sessions.events.send(
    session.id,
    events=[{
        "type": "user.message",
        "content": [{"type": "text", "text": "Summarize the codebase"}]
    }]
)
```

## Streaming Events

```python
with client.beta.sessions.events.stream(session.id) as stream:
    for event in stream:
        print(event.type, event)
```

## Updating Agent Configuration Mid-Session

```python
client.beta.sessions.update(
    session.id,
    agent={
        "tools": [
            {"type": "agent_toolset_20260401"},
            {"type": "mcp_toolset", "mcp_server_name": "linear"},
        ],
        "mcp_servers": [{"type": "url", "name": "linear", "url": "https://mcp.linear.app/sse"}],
    },
    vault_ids=["vlt_..."],
)
```

## Agent Versioning

Each `POST /v1/agents/{id}` (update) creates a new immutable version. The agent's history is append-only.

```python
# Pin to specific version
session = client.beta.sessions.create(
    agent={"type": "agent", "id": agent_id, "version": agent_version},
    environment_id=environment_id,
)
```

## Agent Endpoints

| Operation | Method | Path |
| --- | --- | --- |
| Create | `POST` | `/v1/agents` |
| List | `GET` | `/v1/agents` |
| Get | `GET` | `/v1/agents/{id}` |
| Update | `POST` | `/v1/agents/{id}` |
| Archive | `POST` | `/v1/agents/{id}/archive` |

## Common Pitfalls

- **Agent FIRST, then session — NO EXCEPTIONS** — `model`, `system`, `tools` are **top-level fields on `POST /v1/agents`**, never on `sessions.create()`
- **Agent ONCE, not every run** — store the returned `agent_id` and reuse it
- **MCP auth goes through vaults** — the agent's `mcp_servers` array declares URLs only; credentials live in vaults
- **Reconcile resources before the first run** — missing tool, credential, data mount, or context = agent flails mid-run
- **Stream to get events** — `GET /v1/sessions/{id}/events/stream` is the primary way to receive agent output
- **Archive is permanent on every resource** — archiving makes it read-only with no unarchive. Do NOT archive as routine cleanup.

## TypeScript Example

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

// 1. Create the agent (reusable, versioned)
const agent = await client.beta.agents.create({
  name: "Coding Assistant",
  model: "claude-opus-4-8",
  system: "You are a helpful coding agent.",
  tools: [{ type: "agent_toolset_20260401" }],
});

// 2. Start a session that references it
const session = await client.beta.sessions.create({
  agent: agent.id,
  environment_id: environmentId,
  title: "Hello World Session",
});

console.log(`Session URL: https://platform.claude.com/workspaces/default/sessions/${session.id}`);
```

## Vaults (MCP Credentials)

Vaults store credentials (MCP auth, API keys) with auto-refresh. Reference them in sessions via `vault_ids`.

```python
# Create a vault with OAuth credentials
vault = client.beta.vaults.create(name="GitHub MCP Vault")
credential = client.beta.vaults.credentials.create(
    vault.id,
    type="mcp_oauth",
    mcp_server_name="github",
    # ... OAuth details
)

# Reference vault in session
session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment_id,
    vault_ids=[vault.id],
)
```

## Scheduled Deployments (Cron)

```python
deployment = client.beta.deployments.create(
    agent_id=agent_id,
    environment_id=environment_id,
    schedule="0 * * * *",  # every hour
    title="Hourly Report",
    initial_message="Generate the hourly status report.",
)
```
