# OpenAI Models Overview
> Source: https://platform.openai.com/docs/models
> Fetched: 2026-06-20

## Current Model Families

### GPT-4o Series (Multimodal Flagship)

| Model ID | Context Window | Vision | Tool Calling | Notes |
|----------|---------------|--------|--------------|-------|
| `gpt-4o` | 128k tokens | Yes | Yes | Latest multimodal flagship |
| `gpt-4o-mini` | 128k tokens | Yes | Yes | Cost-efficient, fast |
| `gpt-4o-audio-preview` | 128k tokens | No | Yes | Audio input/output |

**gpt-4o** is the primary multimodal model for most use cases — fast, capable, supports text, image, and audio modalities. Good for chat, coding, vision tasks, and general reasoning.

**gpt-4o-mini** is a smaller, cheaper version of GPT-4o designed for simpler tasks that still require speed and vision support.

### GPT-4.1 Series (Latest Generation)

| Model ID | Context Window | Vision | Tool Calling | Notes |
|----------|---------------|--------|--------------|-------|
| `gpt-4.1` | 1,000,000 tokens | Yes | Yes | Best coding + instruction following |
| `gpt-4.1-mini` | 1,000,000 tokens | Yes | Yes | Efficient, 1M context |
| `gpt-4.1-nano` | 1,000,000 tokens | Yes | Yes | Smallest/cheapest 4.1 variant |

The GPT-4.1 family outperforms GPT-4o across coding and instruction-following benchmarks. Their **1 million token context window** is a major upgrade for long-document workflows. Improved long-context comprehension vs. prior models.

### o-Series Reasoning Models

| Model ID | Context Window | Vision | Tool Calling | Strengths |
|----------|---------------|--------|--------------|-----------|
| `o3` | 200k tokens | Yes | Yes | Hardest math/science/coding problems |
| `o4-mini` | 200k tokens | Yes | Yes | High-volume reasoning, lower cost |
| `o3-mini` | 200k tokens | No | Yes | Science, math, coding (compact) |
| `o1` | 200k tokens | Yes | Yes | Original strong reasoning model |
| `o1-mini` | 128k tokens | No | Yes | Smaller o1 variant |

Reasoning models ("o-series") use chain-of-thought internally before producing output. They excel at multi-step problems: advanced math, science benchmarks, complex coding, and technical writing. 

**o3** sets a new standard on the hardest reasoning tasks. **o4-mini** offers significantly higher usage limits than o3, making it a strong high-volume, high-throughput option. Both o3 and o4-mini can use tools (web search, code interpreter, etc.) natively via reinforcement learning training.

### GPT-4.5 (Deprecated)

`gpt-4.5-preview` — retires from ChatGPT on **June 27, 2026**. Use gpt-4.1 instead.

### GPT-5 Series (Newest)

GPT-5 and GPT-5-mini were released in 2026 as the newest flagship generation with improved performance across all categories. Context windows and exact IDs vary — check the latest changelog at https://platform.openai.com/docs/changelog.

## Capability Matrix

| Capability | GPT-4o | GPT-4.1 | o3 | o4-mini | GPT-4o-mini |
|-----------|--------|---------|----|---------|----|
| Vision (images) | Yes | Yes | Yes | Yes | Yes |
| Audio input | Partial | No | No | No | No |
| Streaming | Yes | Yes | Yes | Yes | Yes |
| Tool/function calling | Yes | Yes | Yes | Yes | Yes |
| JSON mode | Yes | Yes | Yes | Yes | Yes |
| Structured Outputs | Yes | Yes | Yes | Yes | Yes |
| System prompt | Yes | Yes | Limited | Limited | Yes |
| Max context | 128k | 1M | 200k | 200k | 128k |

## Model Selection Guide

- **General chat / assistant**: `gpt-4o` or `gpt-4.1`
- **Cost-efficient high-volume**: `gpt-4o-mini` or `gpt-4.1-nano`
- **Long documents (>128k tokens)**: `gpt-4.1` (1M context)
- **Hard math / science / logic**: `o3`
- **Reasoning at scale / high throughput**: `o4-mini`
- **Coding and instruction following**: `gpt-4.1`
- **Vision tasks**: `gpt-4o` or `gpt-4.1`

## Deprecated / Retiring Models

- `gpt-4.5` / `gpt-4.5-preview` — retiring June 27, 2026
- `o3` in ChatGPT — retiring August 26, 2026 (API availability may differ)
- `o4-mini` — reportedly retired from API on February 13, 2026 (check current status)
- Legacy `gpt-4`, `gpt-4-turbo` — superseded by GPT-4o and GPT-4.1

## GPT-5 Series (2026)

The GPT-5 family represents the newest flagship generation as of 2026:

### GPT-5.5 (Latest Flagship — April 2026)
- **Model ID:** `gpt-5.5`, `gpt-5.5-2026-04-23`
- **Context window:** 1,050,000 tokens
- **Max output:** 128,000 tokens
- **Pricing:** $5.00/$30.00 per 1M input/output; cached: $0.50/1M
- **Pricing note:** For prompts >272K tokens: 2x input + 1.5x output for full session

### GPT-5.5 Pro
- **Model ID:** `gpt-5.5-pro`
- **Pricing:** $30.00/$180.00 per 1M input/output
- **Access:** Paid tiers only

### GPT-5.4 (March 2026)
- **Model ID:** `gpt-5.4`
- **Pricing:** $2.50/$15.00 per 1M input/output

### GPT-5.4 Nano
- **Model ID:** `gpt-5.4-nano`
- **Pricing:** $0.20/$1.25 per 1M input/output

### GPT-5
- **Model ID:** `gpt-5`
- **Pricing:** $1.25/$10.00 per 1M input/output

### GPT-5 Mini
- **Model ID:** `gpt-5-mini`
- **Pricing:** $0.25/$2.00 per 1M input/output

## o1 Specifics

### o1 Pro
- **Model ID:** `o1-pro`
- **Use case:** Maximum reasoning, highest accuracy

### Key o1 Limitations vs GPT Models
- Does NOT support `temperature`, `top_p`, `presence_penalty`, `frequency_penalty`
- Does NOT support system messages (use `"developer"` role)
- Reasoning tokens are generated internally and charged but not visible by default
- Use `max_completion_tokens` (not `max_tokens`) to include reasoning token budget

## Pricing Summary (Complete, June 2026)

| Model | Input ($/1M) | Output ($/1M) | Cached ($/1M) |
|-------|-------------|--------------|---------------|
| gpt-5.5 | $5.00 | $30.00 | $0.50 |
| gpt-5.5-pro | $30.00 | $180.00 | — |
| gpt-5.4 | $2.50 | $15.00 | ~$0.25 |
| gpt-5.4-nano | $0.20 | $1.25 | — |
| gpt-5 | $1.25 | $10.00 | — |
| gpt-5-mini | $0.25 | $2.00 | — |
| gpt-4.1 | $2.00 | $8.00 | $0.50 |
| gpt-4.1-mini | $0.40 | $1.60 | $0.10 |
| gpt-4.1-nano | $0.10 | $0.40 | $0.025 |
| gpt-4o | $2.50 | $10.00 | $1.25 |
| gpt-4o-mini | $0.15 | $0.60 | $0.075 |
| o1 | $15.00 | $60.00 | $7.50 |
| o1-mini | $3.00 | $12.00 | — |
| o3 | $2.00 | $8.00 | — |
| o3-mini | $1.10 | $4.40 | — |
| o3-pro | $20.00 | $80.00 | — |
| o4-mini | $1.10 | $4.40 | — |

**Batch API**: 50% off all above prices.

## Sources
- [Models | OpenAI API](https://developers.openai.com/api/docs/models)
- [All models | OpenAI API](https://developers.openai.com/api/docs/all-models)
- [Introducing GPT-4.1 in the API | OpenAI](https://openai.com/index/gpt-4-1/)
- [Introducing OpenAI o3 and o4-mini | OpenAI](https://openai.com/index/introducing-o3-and-o4-mini/)
- [Deprecations | OpenAI API](https://developers.openai.com/api/docs/deprecations)
- [Changelog | OpenAI API](https://platform.openai.com/docs/changelog)
- [Every OpenAI model in 2026 | eesel AI](https://www.eesel.ai/blog/openai-models-list)
- [OpenAI API Pricing 2026 | DevTk.AI](https://devtk.ai/en/blog/openai-api-pricing-guide-2026/)
