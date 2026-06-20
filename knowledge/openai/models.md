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

## Sources
- [Models | OpenAI API](https://developers.openai.com/api/docs/models)
- [All models | OpenAI API](https://developers.openai.com/api/docs/all-models)
- [Introducing GPT-4.1 in the API | OpenAI](https://openai.com/index/gpt-4-1/)
- [Introducing OpenAI o3 and o4-mini | OpenAI](https://openai.com/index/introducing-o3-and-o4-mini/)
- [Deprecations | OpenAI API](https://developers.openai.com/api/docs/deprecations)
- [Changelog | OpenAI API](https://platform.openai.com/docs/changelog)
