# Agent Design Patterns
> Source: https://platform.claude.com/docs/en/build-with-claude/agent-design.md
> Fetched: 2026-06-20
---

## When to Build an Agent

Before choosing the agent tier, check all four criteria:
- **Complexity** — Is the task multi-step and hard to fully specify in advance?
- **Value** — Does the outcome justify higher cost and latency?
- **Viability** — Is Claude capable at this task type?
- **Cost of error** — Can errors be caught and recovered from?

If the answer is "no" to any of these, stay at a simpler tier.

## Which Surface to Use

| Use Case | Tier | Recommended Surface |
| --- | --- | --- |
| Classification, summarization, extraction, Q&A | Single LLM call | **Claude API** |
| Batch processing or embeddings | Single LLM call | **Claude API** |
| Multi-step pipelines with code-controlled logic | Workflow | **Claude API + tool use** |
| Custom agent with your own tools | Agent | **Claude API + tool use** |
| Server-managed stateful agent with workspace | Agent | **Managed Agents** |
| Persisted, versioned agent configs | Agent | **Managed Agents** |
| Long-running multi-turn agent with file mounts | Agent | **Managed Agents** |

**Cloud-provider access:** For feature availability on Amazon Bedrock, Google Vertex AI, and Microsoft Foundry, see `platform-availability.md`.

## Model Parameters

| Parameter | When to use it | What to expect |
| --- | --- | --- |
| **Adaptive thinking** (`thinking: {type: "adaptive"}`) | When you want Claude to control when and how much to think. | Claude determines thinking depth per request automatically. |
| **Effort** (`output_config: {effort: ...}`) | When adjusting the tradeoff between thoroughness and token efficiency. | Lower effort → fewer tool calls, terser confirmations. `medium` is often a favorable balance. Use `max` when correctness matters. |

## Designing Your Tool Surface

### Bash vs. dedicated tools

A **bash tool** gives Claude broad programmatic leverage. A **dedicated tool** gives the harness a typed hook it can intercept, gate, render, or audit.

**When to promote an action to a dedicated tool:**
- **Security boundary** — Hard-to-reverse actions (external API calls, sending messages, deleting data) can be gated behind user confirmation.
- **Staleness checks** — A dedicated `edit` tool can reject writes if the file changed since Claude last read it.
- **Rendering** — Some actions benefit from custom UI. (Claude Code promotes question-asking to a tool so it can render as a modal.)
- **Scheduling** — Read-only tools can be marked parallel-safe.

**Rule of thumb:** Start with bash for breadth. Promote to dedicated tools when you need to gate, render, audit, or parallelize the action.

## Anthropic-Provided Tools

| Tool | Side | When to use it |
| --- | --- | --- |
| **Bash** | Client | Claude needs to execute shell commands. |
| **Text editor** | Client | Claude needs to read or edit files. |
| **Computer use** | Client or Server | Claude needs to interact with GUIs, web apps, or visual interfaces. |
| **Code execution** | Server | Claude needs to run code in a sandbox you don't want to manage. |
| **Web search / fetch** | Server | Claude needs information past its training cutoff. |
| **Memory** | Client | Claude needs to save context across sessions. |

**Client-side** tools are defined by Anthropic but executed by your harness.
**Server-side** tools run entirely on Anthropic infrastructure — declare them in `tools` and Claude handles the rest.

## Composing Tool Calls: Programmatic Tool Calling

**Programmatic tool calling (PTC)** lets Claude compose sequential tool calls into a script instead. The script runs in the code execution container. When the script calls a tool, the container pauses, the call executes, and the result returns to the running code — not to Claude's context. Only the script's final output returns to Claude.

| When to use it | What to expect |
| --- | --- |
| Many sequential tool calls, or large intermediate results you want filtered before they hit the context window. | Claude writes code that invokes tools as functions. Token cost scales with final output, not intermediate results. |

## Scaling the Tool and Instruction Set

| Feature | When to use it |
| --- | --- |
| **Tool search** | Many tools available, but only a few relevant per request. Don't want all schemas in context upfront. |
| **Skills** | Task-specific instructions Claude should load only when relevant. |

Both patterns keep the fixed context small and load detail on demand.

## Long-Running Agents: Managing Context

| Pattern | When to use it | What to expect |
| --- | --- | --- |
| **Context editing** | Context grows stale over many turns (old tool results, completed thinking). | Tool results and thinking blocks are cleared based on configurable thresholds. |
| **Compaction** | Conversation likely to reach or exceed the context window limit. | Earlier context is summarized into a compaction block server-side. |
| **Memory** | State must persist across sessions. | Claude reads/writes files in a memory directory. Survives process restarts. |

**Choosing between them:** Context editing and compaction operate within a session — editing prunes stale turns, compaction summarizes when you're near the limit. Memory is for cross-session persistence. Many long-running agents use all three.

## Caching for Agents

**Read prompt-caching.md first.** Agent-specific workarounds:

| Constraint | Agent-specific workaround |
| --- | --- |
| Editing the system prompt mid-session invalidates the cache. | Append a `{"role": "system", ...}` message to `messages[]` instead. |
| Switching models mid-session invalidates the cache. | Spawn a **subagent** with the cheaper model for the sub-task. |
| Adding/removing tools mid-session invalidates the cache. | Use **tool search** for dynamic discovery — it appends tool schemas rather than swapping them. |

## Tool Security

### Bash tool security
- Run in an isolated environment (container, VM, or restricted user)
- Apply an **allowlist** of permitted executables
- Reject shell operators (`&&`, `|`, `;`, backticks, `$()`)
- Set timeouts and resource limits
- Log every command
- A blocklist is NOT sufficient

### Text editor tool security
- **Confine every file operation to a fixed project root**
- Resolve the model-supplied `path` to its canonical form and verify it remains within your project root
- Reject `..`, symlinks, absolute paths outside the root, URL-encoded traversal
- Use Python `pathlib.Path.resolve()` then check `.is_relative_to(root)`

### Code execution security
- Always sanitize filenames with `os.path.basename()` before writing downloaded files
- Write files to a dedicated output directory
- Never trust model-generated file paths directly

## Agentic Loop Design Principles

1. **Set a `max_continuations` limit** (e.g., 5) to prevent infinite loops
2. **Always check `stop_reason`** before reading `content`
3. **Handle `pause_turn`** — re-send the user message and assistant response to continue server-side tool loops
4. **Log every tool call** — this is critical for debugging and auditing
5. **Validate tool inputs** within your tool functions before executing
6. **Return informative error messages** on failure so Claude can adapt
7. **Consider human-in-the-loop approval** for tools with side effects

## Context Window Management

- 1M context window for Opus 4.8, Opus 4.7, Opus 4.6, Sonnet 4.6, Fable 5
- 200K context window for Haiku 4.5
- Use compaction (`compact-2026-01-12` beta) to handle conversations approaching limits
- Use context editing (`context-management-2025-06-27` beta) to clear stale tool results
- **CRITICAL:** When using compaction, append `response.content` (not just text) to preserve compaction blocks

## Multi-Agent Patterns

For **Managed Agents**, use the `multiagent` field on `agents.create()`:

```python
agent = client.beta.agents.create(
    name="Coordinator Agent",
    model="claude-opus-4-8",
    system="You coordinate work across specialized agents.",
    tools=[{"type": "agent_toolset_20260401"}],
    multiagent={
        "type": "coordinator",
        "agents": ["agent_abc123", "agent_def456"]
    },
)
```

For **Messages API** multi-agent patterns, spawn subagents as separate API calls and coordinate results in your code.
