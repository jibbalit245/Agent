# Model Migration Guide
> Source: https://platform.claude.com/docs/en/about-claude/models/migration-guide.md
> Fetched: 2026-06-20
---

## Quick Reference

**TL;DR:** Change the model ID string. If you were using `budget_tokens`, switch to `thinking: {type: "adaptive"}`. If you were using assistant prefills, they 400 on Opus 4.6 and Sonnet 4.6 — switch to `output_config.format`. Remove GA beta headers.

## Destination Models (recommended targets)

| If you're on…                           | Migrate to         | Why                                               |
| --------------------------------------- | ------------------ | ------------------------------------------------- |
| Opus 4.7                                | `claude-opus-4-8`  | Most capable Opus-tier model; same API surface as 4.7 |
| Opus 4.6                                | `claude-opus-4-8`  | Apply the Opus 4.7 breaking changes, then the 4.8 re-tuning |
| Opus 4.0 / 4.1 / 4.5 / Opus 3          | `claude-opus-4-8`  | Apply 4.6 → 4.7 → 4.8 in order |
| Sonnet 4.0 / 4.5 / 3.7 / 3.5           | `claude-sonnet-4-6`| Best speed / intelligence balance; adaptive thinking; 64K output |
| Haiku 3 / 3.5                           | `claude-haiku-4-5` | Fastest and most cost-effective                   |
| Claude Mythos Preview                   | `claude-mythos-5` or `claude-fable-5` | Same tokenizer family |

## Retired Model Replacements (return 404)

| Retired model                 | Retired       | Drop-in replacement  |
| ----------------------------- | ------------- | -------------------- |
| `claude-3-7-sonnet-20250219`  | Feb 19, 2026  | `claude-sonnet-4-6`  |
| `claude-3-5-haiku-20241022`   | Feb 19, 2026  | `claude-haiku-4-5`   |
| `claude-3-opus-20240229`      | Jan 5, 2026   | `claude-opus-4-8`    |
| `claude-3-5-sonnet-20241022`  | Oct 28, 2025  | `claude-sonnet-4-6`  |
| `claude-3-5-sonnet-20240620`  | Oct 28, 2025  | `claude-sonnet-4-6`  |
| `claude-3-sonnet-20240229`    | Jul 21, 2025  | `claude-sonnet-4-6`  |
| `claude-2.1`, `claude-2.0`    | Jul 21, 2025  | `claude-sonnet-4-6`  |

## Breaking Changes by Model

### Migrating to Opus 4.7 (from Opus 4.6)

**Breaking: `budget_tokens` returns 400.** Use `thinking: {type: "adaptive"}` instead.

**Breaking: `temperature`, `top_p`, `top_k` return 400.** Remove them.

```python
# Before (Opus 4.6)
client.messages.create(
    model="claude-opus-4-6",
    max_tokens=64000,
    thinking={"type": "enabled", "budget_tokens": 32000},
    temperature=0.7,  # This will 400 on 4.7
    messages=[...]
)

# After (Opus 4.7)
client.messages.create(
    model="claude-opus-4-7",
    max_tokens=64000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    messages=[...]
)
```

**Silent change: Thinking content omitted by default on Opus 4.7.** Opt in with `thinking.display: "summarized"`:

```python
thinking={"type": "adaptive", "display": "summarized"}
```

**New feature: Task Budgets (beta) on Opus 4.7:**

```python
client.beta.messages.create(
    betas=["task-budgets-2026-03-13"],
    model="claude-opus-4-7",
    max_tokens=64000,
    thinking={"type": "adaptive"},
    output_config={
        "effort": "high",
        "task_budget": {"type": "tokens", "total": 128000},
    },
    messages=[...],
)
```

### Migrating to Opus 4.6 / Sonnet 4.6 (from older models)

**1. Manual extended thinking is deprecated — use adaptive thinking.**

```python
# Old (deprecated)
thinking={"type": "enabled", "budget_tokens": 8000}

# New
thinking={"type": "adaptive"}
output_config={"effort": "high"}  # optional: low | medium | high | max
```

**2. Effort parameter.** Goes inside `output_config`, not top-level. Default is `high`. `max` is Opus-tier only.

**3. Assistant-turn prefills return 400 on Opus 4.6 and Sonnet 4.6.**

| Prefill was used for | Replacement |
| -------------------- | ----------- |
| Forcing JSON / YAML / schema output | `output_config.format` with a `json_schema` |
| Forcing a classification label | Tool with an enum field, or structured outputs |
| Skipping preambles | System prompt instruction: "Respond directly without preamble." |
| Steering around bad refusals | Usually no longer needed on 4.6 |

```python
# Old (fails on Opus 4.6 / Sonnet 4.6)
messages=[
    {"role": "user", "content": "Extract the name."},
    {"role": "assistant", "content": "{\"name\": \""},  # PREFILL — 400 on 4.6
]

# New
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    output_config={"format": {"type": "json_schema", "schema": {...}}},
    messages=[{"role": "user", "content": "Extract the name."}],
)
```

**4. Stream for `max_tokens > ~16K`.**

```python
with client.messages.stream(model="claude-opus-4-6", max_tokens=64000, ...) as stream:
    message = stream.get_final_message()
```

### When Coming from 3.x / 4.0 / 4.1 (additional changes)

1. `temperature` OR `top_p`, not both (passing both errors on Claude 4+)
2. Update tool versions — both `type` AND `name` change:
   - `text_editor_20250124` + `str_replace_editor` → `text_editor_20250728` + `str_replace_based_edit_tool`
   - `code_execution_20250825` for code execution
   - Delete `undo_edit` command call sites
3. Handle `stop_reason == "refusal"` (new on Claude 4+)
4. Handle `stop_reason == "model_context_window_exceeded"` (new on 4.5+)

## Beta Headers to Remove on 4.6

| Header | Action |
| --- | --- |
| `effort-2025-11-24` | Remove (effort is now GA) |
| `fine-grained-tool-streaming-2025-05-14` | Remove (GA) |
| `interleaved-thinking-2025-05-14` | Remove when using adaptive thinking |
| `token-efficient-tools-2025-02-19` | Remove (built in to Claude 4+) |
| `output-128k-2025-02-19` | Remove (built in to Claude 4+) |

Switch from `client.beta.messages.create(...)` back to `client.messages.create(...)` once all betas are removed.

## Per-SDK Syntax Reference

### `thinking` — `budget_tokens` → adaptive

| SDK | Before | After |
|---|---|---|
| Python | `thinking={"type": "enabled", "budget_tokens": N}` | `thinking={"type": "adaptive"}` |
| TypeScript | `thinking: { type: 'enabled', budget_tokens: N }` | `thinking: { type: 'adaptive' }` |
| Go | `Thinking: anthropic.ThinkingConfigParamOfEnabled(N)` | `Thinking: anthropic.ThinkingConfigParamUnion{OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{}}` |
| Ruby | `thinking: { type: "enabled", budget_tokens: N }` | `thinking: { type: "adaptive" }` |
| Java | `.thinking(ThinkingConfigEnabled.builder().budgetTokens(N).build())` | `.thinking(ThinkingConfigAdaptive.builder().build())` |
| C# | `Thinking = new ThinkingConfigEnabled { BudgetTokens = N }` | `Thinking = new ThinkingConfigAdaptive()` |
| PHP | `thinking: ['type' => 'enabled', 'budget_tokens' => N]` | `thinking: ['type' => 'adaptive']` |

### Effort Level Guide (Opus 4.7)

| Level | Use when |
| --- | --- |
| `max` | Intelligence-demanding tasks worth testing at the ceiling |
| `xhigh` | **Most coding and agentic use cases** (default in Claude Code) |
| `high` | Intelligence-sensitive use cases generally |
| `medium` | Cost-sensitive use cases that need to reduce token usage |
| `low` | Short, scoped tasks and latency-sensitive workloads |

## Migrating to Claude Fable 5

- **Thinking is always on** — omit the `thinking` parameter entirely (or send `{type: "adaptive"}`). `{type: "disabled"}` and `{type: "enabled", budget_tokens: N}` both return a 400.
- **The raw chain of thought is never returned** — `display: "summarized"` returns a readable summary, `"omitted"` (default) leaves `thinking` field as empty string.
- **`refusal` stop reason** — safety classifiers may decline a request. Always check `stop_reason` before reading `content`.
- **Include fallbacks by default** for Fable 5 code:

```python
response = client.beta.messages.create(
    model="claude-fable-5",
    max_tokens=16000,
    betas=["server-side-fallback-2026-06-01"],
    fallbacks=[{"model": "claude-opus-4-8"}],
    messages=[{"role": "user", "content": "..."}],
)
```

- **No assistant prefill** — same as the rest of the 4.6+ family.
- **30-day data retention required** — not available under zero data retention.
- **Requires `output_config.effort`** for performance control (same `low`/`medium`/`high`/`xhigh`/`max` scale).

## Migration Checklist

**Every migration (BLOCKS = causes 400 error):**
- [ ] **[BLOCKS]** Update the `model=` string
- [ ] **[BLOCKS]** Replace `budget_tokens` with `thinking={"type": "adaptive"}`
- [ ] **[BLOCKS]** Move `format` from `output_format` into `output_config.format`
- [ ] **[BLOCKS]** Remove any assistant-turn prefills if targeting Opus 4.6 or Sonnet 4.6
- [ ] **[BLOCKS]** Switch to streaming if `max_tokens > ~16000`
- [ ] **[TUNE]** Set `output_config={"effort": "..."}` explicitly
- [ ] **[TUNE]** Remove GA beta headers
- [ ] **[TUNE]** Switch `client.beta.messages.create(...)` → `client.messages.create(...)`
- [ ] **[TUNE]** Review system prompt for aggressive tool language

**Extra items when coming from 3.x / 4.0 / 4.1:**
- [ ] **[BLOCKS]** Remove either `temperature` or `top_p` (passing both 400s on Claude 4+)
- [ ] **[BLOCKS]** Update text-editor tool `type` to `text_editor_20250728`
- [ ] **[BLOCKS]** Update text-editor tool `name` to `str_replace_based_edit_tool`
- [ ] **[BLOCKS]** Update code-execution tool to `code_execution_20250825`
- [ ] **[BLOCKS]** Delete any `undo_edit` command call sites
- [ ] **[TUNE]** Add handling for `stop_reason == "refusal"`
- [ ] **[TUNE]** Add handling for `stop_reason == "model_context_window_exceeded"`

## Amazon Bedrock Model IDs

On Bedrock, model IDs carry an `anthropic.` provider prefix:

```python
# First-party ID
model="claude-opus-4-8"

# Bedrock ID
model="anthropic.claude-opus-4-8"
```

## Prompt-Behavior Changes (Opus 4.5 / 4.6, Sonnet 4.6)

1. **Aggressive instructions cause overtriggering** — dial back `CRITICAL:`, `MUST`, `If in doubt` language
2. **Overthinking and excessive exploration at higher effort** — lower effort to `medium` first
3. **Design and frontend coding** — Opus 4.7 has a default house style (cream backgrounds, serif type); use explicit specs to override
4. **Uses tools less often by default on Opus 4.7** — raise effort or add tool descriptions with explicit trigger conditions
