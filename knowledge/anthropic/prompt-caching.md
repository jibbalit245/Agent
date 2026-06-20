# Prompt Caching — Design & Optimization
> Source: https://platform.claude.com/docs/en/build-with-claude/prompt-caching.md
> Fetched: 2026-06-20
---

## The One Invariant Everything Follows From

**Prompt caching is a prefix match. Any change anywhere in the prefix invalidates everything after it.**

The cache key is derived from the exact bytes of the rendered prompt up to each `cache_control` breakpoint. A single byte difference at position N — a timestamp, a reordered JSON key, a different tool in the list — invalidates the cache for all breakpoints at positions ≥ N.

Render order is: `tools` → `system` → `messages`. A breakpoint on the last system block caches both tools and system together.

## API Reference

```json
"cache_control": {"type": "ephemeral"}              // 5-minute TTL (default)
"cache_control": {"type": "ephemeral", "ttl": "1h"} // 1-hour TTL
```

- Max **4** `cache_control` breakpoints per request.
- Goes on any content block: system text blocks, tool definitions, message content blocks (`text`, `image`, `tool_use`, `tool_result`, `document`).
- Top-level `cache_control` on `messages.create()` auto-places on the last cacheable block.

### Minimum Cacheable Prefix by Model

| Model | Minimum |
|---|---:|
| Opus 4.8, Opus 4.7, Opus 4.6, Opus 4.5, Haiku 4.5 | 4096 tokens |
| Fable 5, Sonnet 4.6, Haiku 3.5, Haiku 3 | 2048 tokens |
| Sonnet 4.5, Sonnet 4.1, Sonnet 4, Sonnet 3.7 | 1024 tokens |

A 3K-token prompt caches on Sonnet 4.5 and Fable 5 but silently won't on Opus 4.8.

### Economics

- Cache reads cost ~0.1× base input price
- Cache writes: **1.25× for 5-minute TTL, 2× for 1-hour TTL**
- With 5-minute TTL: two requests break even (1.25× + 0.1× = 1.35× vs 2× uncached)
- With 1-hour TTL: need at least three requests (2× + 0.2× = 2.2× vs 3× uncached)

## Placement Patterns

### Large system prompt shared across many requests

```json
"system": [
  {"type": "text", "text": "<large shared prompt>", "cache_control": {"type": "ephemeral"}}
]
```

### Automatic Caching (Recommended)

```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    cache_control={"type": "ephemeral"},  # auto-caches the last cacheable block
    system="You are an expert on this large document...",
    messages=[{"role": "user", "content": "Summarize the key points"}]
)
```

### Multi-turn conversations

Put a breakpoint on the last content block of the most-recently-appended turn:

```json
// Last content block of the last user turn
messages[-1].content[-1].cache_control = {"type": "ephemeral"}
```

### Shared prefix, varying suffix

```json
"messages": [{"role": "user", "content": [
  {"type": "text", "text": "<shared context>", "cache_control": {"type": "ephemeral"}},
  {"type": "text", "text": "<varying question>"}  // no marker — differs every time
]}]
```

### Mid-conversation system messages (Claude Opus 4.8 only)

Send operator instructions mid-conversation as `{"role": "system", "content": "..."}` appended to `messages[]`, rather than editing top-level `system`. This preserves the cached prefix.

```json
"system": [{"type": "text", "text": "<stable core>", "cache_control": {"type": "ephemeral"}}],
"messages": [
  ...history,
  {"role": "user", "content": "..."},
  {"role": "system", "content": "Terse mode enabled — keep responses under 40 words."}
]
```

## Verifying Cache Hits

```python
print(response.usage.cache_creation_input_tokens)  # tokens written to cache (~1.25x cost)
print(response.usage.cache_read_input_tokens)      # tokens served from cache (~0.1x cost)
print(response.usage.input_tokens)                 # uncached tokens (full cost)
```

- `input_tokens` is the uncached remainder only
- Total prompt size = `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`

## Silent Invalidators

When reviewing code, grep for these inside anything that feeds the prompt prefix:

| Pattern | Why it breaks caching |
|---|---|
| `datetime.now()` / `Date.now()` / `time.time()` in system prompt | Prefix changes every request |
| `uuid4()` / `crypto.randomUUID()` / request IDs early in content | Same — every request is unique |
| `json.dumps(d)` without `sort_keys=True` / iterating a `set` | Non-deterministic serialization |
| f-string interpolating session/user ID into system prompt | Per-user prefix; no cross-user sharing |
| `tools=build_tools(user)` where set varies per user | Tools render at position 0 |

## Architectural Guidance

**Keep the system prompt frozen.** Don't interpolate "current date: X", "mode: Y" into the system prompt. Inject dynamic context later in `messages` instead.

**Don't change tools or model mid-conversation.** Tools render at position 0; adding, removing, or reordering a tool invalidates the entire cache.

**Fork operations must reuse the parent's exact prefix.** Copy the parent's `system`, `tools`, and `model` verbatim, then append fork-specific content at the end.

## Pre-warming the Cache

To eliminate cache-miss latency on the first real request, send a `max_tokens: 0` request at startup:

```python
client.messages.create(
    model="claude-opus-4-8",
    max_tokens=0,
    system=[{
        "type": "text",
        "text": SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},
    }],
    messages=[{"role": "user", "content": "warmup"}],
)
```

**Rejected combinations:** `max_tokens: 0` is an `invalid_request_error` with `stream: true`, `thinking.type: "enabled"`, `output_config.format`, or specific `tool_choice` values.

## 20-Block Lookback Window

Each breakpoint walks backward **at most 20 content blocks** to find a prior cache entry. If a single turn adds more than 20 blocks (common in agentic loops with many tool_use/tool_result pairs), the next request's breakpoint won't find the previous cache and silently misses.

Fix: place an intermediate breakpoint every ~15 blocks in long turns.

## Concurrent-Request Timing

A cache entry becomes readable only after the first response **begins streaming**. N parallel requests with identical prefixes all pay full price.

For fan-out patterns: send 1 request, await the first streamed token, then fire the remaining N−1.

## Invalidation Hierarchy

| Change | Tools cache | System cache | Messages cache |
|---|:---:|:---:|:---:|
| Tool definitions (add/remove/reorder) | ❌ | ❌ | ❌ |
| Model switch | ❌ | ❌ | ❌ |
| System prompt content | ✅ | ❌ | ❌ |
| `tool_choice`, images, `thinking` enable/disable | ✅ | ✅ | ❌ |
| Message content | ✅ | ✅ | ❌ |
