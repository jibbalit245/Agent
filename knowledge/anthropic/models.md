# Anthropic Claude Models Overview
> Source: https://docs.anthropic.com/en/docs/about-claude/models
> Fetched: 2026-06-20

## Current Models (Active as of June 2026)

| Model | API ID | Context Window | Max Output | Key Features |
|-------|--------|----------------|------------|--------------|
| Claude Fable 5 | `claude-fable-5` | 1M tokens | 128K tokens | Most capable, thinking always on, new tokenizer (~30% more tokens vs Opus-tier), Project Glasswing public version |
| Claude Mythos 5 | `claude-mythos-5` | 1M tokens | 128K tokens | Invitation-only (Project Glasswing), same capability as Fable 5 |
| Claude Opus 4.8 | `claude-opus-4-8` | 1M tokens | 128K tokens | Current flagship Opus, adaptive thinking, autonomous agentic work |
| Claude Opus 4.7 | `claude-opus-4-7` | 1M tokens | 128K tokens | Previous-gen Opus, adaptive thinking |
| Claude Opus 4.6 | `claude-opus-4-6` | 1M tokens | 128K tokens | Older Opus, adaptive thinking |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M tokens | 64K tokens | Best speed/intelligence balance, adaptive thinking |
| Claude Haiku 4.5 | `claude-haiku-4-5` | 200K tokens | 64K tokens | Fastest, most cost-effective, simple tasks |

## Legacy / Deprecated Models

| Model | API ID | Status |
|-------|--------|--------|
| Claude Opus 4.5 | `claude-opus-4-5` | Active (legacy) |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` | Active (legacy) |
| Claude Opus 4.1 | `claude-opus-4-1` | Deprecated — retires 2026-08-05 |
| Claude Sonnet 4.0 | `claude-sonnet-4-0` | Deprecated |
| Claude Opus 4.0 | `claude-opus-4-0` | Deprecated |
| Claude Haiku 3 | — | Deprecated — retired April 19, 2026 |

## Model Capabilities

### Thinking / Reasoning
- **Fable 5 / Mythos 5**: Thinking always on (cannot be disabled)
- **Opus 4.x and Sonnet 4.6**: Adaptive thinking (can be enabled/disabled)
- **Haiku 4.5**: Standard (no extended thinking)

### Vision (Image Input)
All current models support image input. Supported formats: JPEG, PNG, GIF, WebP.

### Tool Use / Function Calling
All current models support tool use. Claude 4 models have built-in token-efficient tool use and improved parallel tool calling.

### Streaming
All models support server-sent events (SSE) streaming.

### Structured Outputs
All current models support structured outputs (JSON mode).

## Key Specifications

- **Context Window**: 1M tokens standard (Haiku 4.5 has 200K)
- **Max Output**: 128K tokens (Opus/Fable); 64K tokens (Sonnet/Haiku)
- **Tokenizer Note**: Fable 5 uses ~30% more tokens than Opus-tier for the same content due to a new tokenizer
- **Data Retention**: Fable 5 requires 30-day data retention (not available under Zero Data Retention / ZDR agreements)

## Programmatic Model Discovery

Query the Models API for live capability data:

```python
import anthropic

client = anthropic.Anthropic()
m = client.models.retrieve("claude-opus-4-8")

m.id                 # "claude-opus-4-8"
m.display_name       # "Claude Opus 4.8"
m.max_input_tokens   # context window size
m.max_tokens         # max output tokens

# Check capabilities
caps = m.capabilities
caps["image_input"]["supported"]                     # vision support
caps["thinking"]["types"]["adaptive"]["supported"]   # adaptive thinking
caps["effort"]["max"]["supported"]                   # effort control
caps["structured_outputs"]["supported"]              # JSON mode
```

List all available models:
```python
models = client.models.list()
for model in models.data:
    print(model.id, model.display_name)
```

## Recommended Model Selection

- **Autonomous agents / complex reasoning**: `claude-opus-4-8`
- **Balanced speed + quality (most use cases)**: `claude-sonnet-4-6`
- **Fast, cheap, high-volume tasks**: `claude-haiku-4-5`
- **Maximum capability (if available)**: `claude-fable-5`

**Always use exact model IDs — never guess or construct them.**
