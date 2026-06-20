# Context Management
> Source: https://platform.claude.com/docs/en/build-with-claude/context-management.md
> Fetched: 2026-06-20
---

## Overview

For long-running agents and conversations that approach the context window limit, Claude provides two server-side mechanisms: **context editing** and **compaction**. For cross-session persistence, use **memory files**.

## Context Windows

| Model | Context Window |
|---|---|
| Claude Opus 4.8 | 1,000,000 tokens |
| Claude Opus 4.7 | 1,000,000 tokens |
| Claude Opus 4.6 | 1,000,000 tokens |
| Claude Sonnet 4.6 | 1,000,000 tokens |
| Claude Haiku 4.5 | 200,000 tokens |

## Context Editing (`context-management-2025-06-27` Beta)

Context editing clears stale content from the conversation: old tool results, completed thinking blocks, and intermediate steps you no longer need.

### Enable the Beta

```python
response = client.beta.messages.create(
    betas=["context-management-2025-06-27"],
    model="claude-opus-4-8",
    max_tokens=4096,
    messages=messages,
    context_management={
        "edits": [...]
    }
)
```

### Edit Types

#### Clear Tool Results

Remove tool result content after they've been incorporated into the assistant's reasoning:

```python
context_management={
    "edits": [{
        "type": "clear_tool_results_20260627",
        "threshold": {
            "type": "token_count",
            "token_count": 2000  # clear results larger than 2000 tokens
        }
    }]
}
```

#### Clear Thinking Blocks

Remove completed thinking blocks to free space:

```python
context_management={
    "edits": [{
        "type": "clear_thinking_20260627"
    }]
}
```

#### Combined Edits

```python
context_management={
    "edits": [
        {"type": "clear_tool_results_20260627", "threshold": {"type": "token_count", "token_count": 1000}},
        {"type": "clear_thinking_20260627"}
    ]
}
```

## Compaction (`compact-2026-01-12` Beta)

Compaction summarizes the earlier portion of your conversation into a compact block when you approach the context limit. Unlike context editing (which removes specific items), compaction rewrites the early conversation into a dense summary.

### Basic Compaction

```python
response = client.beta.messages.create(
    betas=["compact-2026-01-12"],
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=messages,
    context_management={
        "edits": [{"type": "compact_20260112"}]
    }
)

# CRITICAL: Append response.content (not just text) to preserve compaction blocks
messages.append({"role": "assistant", "content": response.content})
```

### CRITICAL: Preserving Compaction Blocks

When compaction occurs, the response contains a `compaction_block` in `response.content`. **You must append the full `response.content` list**, not just the text — otherwise the compaction summary is lost and the conversation becomes inconsistent.

```python
# WRONG — loses the compaction block
messages.append({
    "role": "assistant",
    "content": response.content[0].text  # only text, drops compaction block
})

# CORRECT
messages.append({
    "role": "assistant",
    "content": response.content  # full content list including any compaction blocks
})
```

### Compaction in a Full Agent Loop

```python
messages = [{"role": "user", "content": user_input}]

while True:
    response = client.beta.messages.create(
        betas=["compact-2026-01-12"],
        model="claude-opus-4-8",
        max_tokens=16000,
        messages=messages,
        context_management={
            "edits": [{"type": "compact_20260112"}]
        }
    )
    
    # Always append full content (includes compaction blocks if any)
    messages.append({"role": "assistant", "content": response.content})
    
    if response.stop_reason == "end_turn":
        break
    
    if response.stop_reason == "tool_use":
        tool_results = execute_tools(response.content)
        messages.append({"role": "user", "content": tool_results})
    
    elif response.stop_reason == "pause_turn":
        # Re-send for server-side tool loops
        messages = [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response.content},
        ]
    
    elif response.stop_reason == "model_context_window_exceeded":
        # Even with compaction, some conversations can exceed limits
        # Truncate or reset as needed
        break
```

## Choosing: Context Editing vs. Compaction

| Pattern | When to use | What happens |
|---|---|---|
| **Context editing** | Context grows stale (old tool results, completed thinking) | Removes specific items based on configurable thresholds |
| **Compaction** | Approaching context window limit | Summarizes early conversation into a compact block |

**Both can be used together** — context editing prunes ongoing overhead; compaction handles when you approach the limit regardless:

```python
context_management={
    "edits": [
        {"type": "clear_tool_results_20260627", "threshold": {"type": "token_count", "token_count": 2000}},
        {"type": "clear_thinking_20260627"},
        {"type": "compact_20260112"}
    ]
}
```

## Memory for Cross-Session Persistence

Context editing and compaction operate within a session. For state that must survive process restarts, use file-based memory:

```
memory/
  summary.md       ← high-level state
  decisions.md     ← key decisions made
  facts.md         ← discovered facts
```

```python
# At session start, load memory into system prompt
with open("memory/summary.md") as f:
    system = f"Previous context:\n{f.read()}\n\nYou are a helpful assistant."

# At session end, save important state
with open("memory/summary.md", "w") as f:
    f.write(summary_response)
```

Managed Agents provides a managed Memory resource with automatic directory mounting per session.

## Monitoring Context Usage

```python
response = client.messages.create(...)

# Check token usage
print(response.usage.input_tokens)   # tokens in this request
print(response.usage.output_tokens)  # tokens generated

# Check stop reason for context overflow
if response.stop_reason == "model_context_window_exceeded":
    print("Context window full — enable compaction or truncate")
```

## Proactive Context Management Strategy

1. **Count tokens before long operations** using `count_tokens` endpoint
2. **Enable context editing** from the start for agentic loops with many tool calls
3. **Enable compaction** when context is expected to grow large
4. **Monitor `stop_reason`** — handle `"model_context_window_exceeded"` gracefully
5. **Use memory files** for information that must survive between sessions
