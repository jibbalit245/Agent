# Platform Availability
> Source: https://platform.claude.com/docs/en/about-claude/models/overview.md
> Fetched: 2026-06-20
---

Which features work on which provider platform.

Columns: **1P** = first-party Claude API, **P-AWS** = Claude Platform on AWS (Anthropic-operated), **Bedrock** = Amazon Bedrock, **Vertex** = Google Cloud Vertex AI, **Foundry** = Microsoft Foundry. ✅ = GA, β = beta, ❌ = not supported.

| Feature | 1P | P-AWS | Bedrock | Vertex | Foundry | Notes |
|---|---|---|---|---|---|---|
| Messages, streaming, tool use | ✅ | ✅ | ✅ | ✅ | ✅ | Core API |
| PDF input | ✅ | ✅ | ✅ | ✅ | β | |
| Structured outputs / strict tool use | ✅ | ✅ | ✅ | ✅ | β | |
| Adaptive thinking / effort | ✅ | ✅ | ✅ | ✅ | β | |
| Extended thinking | ✅ | ✅ | ✅ | ✅ | β | |
| Prompt caching (5m, 1h) | ✅ | ✅ | ✅ | ✅ | β | |
| Automatic prompt caching | ✅ | ✅ | ❌ | ❌ | β | |
| Token counting | ✅ | ✅ | ✅ | ✅ | β | |
| Citations | ✅ | ✅ | ✅ | ✅ | β | |
| Search results content blocks | ✅ | ✅ | ✅ | ✅ | β | |
| Fine-grained tool streaming | ✅ | ✅ | ✅ | ✅ | ✅ | |
| Compaction | β | β | β | β | β | |
| Context editing | β | β | β | β | β | |
| Context windows (1M) | ✅ | ✅ | ✅ | ✅ | β | |
| `inference_geo` (data residency) | ✅ | ✅ | ❌ | ❌ | ❌ | |
| **Server-side tools** | | | | | | |
| Web search | ✅ | ✅ | ❌ | ✅ | β | Vertex: basic `web_search_20250305` only |
| Web fetch | ✅ | ✅ | ❌ | ❌ | β | |
| Code execution | ✅ | ✅ | ❌ | ❌ | β | |
| Tool search | ✅ | ✅ | ✅ | ✅ | β | Bedrock: InvokeModel API only |
| Advisor tool | β | β | ❌ | ❌ | ❌ | |
| **Client-implemented tools** | | | | | | |
| Bash, text editor, memory | ✅ | ✅ | ✅ | ✅ | β | |
| Computer use | β | β | β | β | β | |
| **Agentic / orchestration** | | | | | | |
| Agent Skills (Messages API) | β | β | ❌ | ❌ | β | |
| Programmatic tool calling | ✅ | ✅ | ❌ | ❌ | β | |
| MCP connector | β | β | ❌ | ❌ | β | |
| Managed Agents | β | β | ❌ | ❌ | ❌ | |
| Self-hosted sandboxes | β | β | ❌ | ❌ | ❌ | |
| **API endpoints** | | | | | | |
| Message Batches | ✅ | ✅ | ❌ | ❌ | ❌ | |
| Files API | β | β | ❌ | ❌ | β | |
| Models API | ✅ | ✅ | ❌ | ❌ | ❌ | |
| **Other** | | | | | | |
| Mid-conversation system messages | ✅ | ✅ | ❌ | ❌ | ❌ | Claude Opus 4.8 only |
| Fast mode | β | ❌ | ❌ | ❌ | ❌ | First-party API only |
| Cache diagnostics | β | ❌ | ❌ | ❌ | ❌ | First-party API only |
| Task budgets | β | β | ❌ | ❌ | ❌ | Beta header `task-budgets-2026-03-13` |

## Amazon Bedrock Model IDs

On Bedrock, model IDs carry an `anthropic.` provider prefix:

| First-party ID | Bedrock ID |
|---|---|
| `claude-opus-4-8` | `anthropic.claude-opus-4-8` |
| `claude-opus-4-7` | `anthropic.claude-opus-4-7` |
| `claude-haiku-4-5` | `anthropic.claude-haiku-4-5` |

**Skip for Bedrock:** code execution tool versioning and Task Budgets.

## Claude Platform on AWS

If the code uses `AnthropicAWS` / `AnthropicAws` clients, it is running on **Claude Platform on AWS** — Anthropic-operated, same-day API parity. Model IDs are **bare first-party strings** (no `anthropic.` prefix). Do **not** add an `anthropic.` prefix (that's Amazon Bedrock, a separate offering).

## Claude API Client Setup

### First-party API

```python
import anthropic
client = anthropic.Anthropic()
```

### Amazon Bedrock

```python
import anthropic
client = anthropic.AnthropicBedrock()
```

### Google Vertex AI

```python
import anthropic
client = anthropic.AnthropicVertex()
```

### Claude Platform on AWS

```python
import anthropic
client = anthropic.AnthropicAWS()
```
