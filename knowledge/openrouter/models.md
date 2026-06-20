# OpenRouter Models
> Source: https://openrouter.ai/models
> Fetched: 2026-06-20

## Overview

OpenRouter provides access to 315+ models from major providers. Model IDs follow the format `{provider}/{model-name}` (or `{provider}/{model-name}:free` for free tier variants).

Browse live model list: https://openrouter.ai/models

## Anthropic Claude Models

| Model ID | Context | Notes |
|----------|---------|-------|
| `anthropic/claude-fable-5` | 1M | Most capable, thinking always on |
| `anthropic/claude-opus-4-8` | 1M | Flagship Opus, adaptive thinking |
| `anthropic/claude-sonnet-4-6` | 1M | Best speed/quality balance |
| `anthropic/claude-haiku-4-5` | 200K | Fastest, cheapest |

## OpenAI Models

| Model ID | Context | Notes |
|----------|---------|-------|
| `openai/gpt-4o` | 128K | OpenAI flagship multimodal |
| `openai/gpt-4o-mini` | 128K | Fast, cheap GPT-4o variant |
| `openai/o3` | 128K | Reasoning model |
| `openai/o4-mini` | 128K | Fast reasoning |

## Google Models

| Model ID | Context | Notes |
|----------|---------|-------|
| `google/gemini-2.5-pro` | 1M | Google's latest flagship |
| `google/gemini-flash-1.5` | 1M | Fast, cheap Gemini |
| `google/gemma-3-27b-it` | 8K | Open-weight Gemma |

## Meta Llama Models

| Model ID | Context | Notes |
|----------|---------|-------|
| `meta-llama/llama-4-maverick` | 1M | Meta's latest flagship |
| `meta-llama/llama-4-scout` | 10M | Huge context window |
| `meta-llama/llama-3.3-70b-instruct` | 128K | Popular open model |
| `meta-llama/llama-3.1-8b-instruct` | 128K | Small, fast Llama |

## DeepSeek Models

| Model ID | Context | Notes |
|----------|---------|-------|
| `deepseek/deepseek-chat` | 64K | DeepSeek V3, strong coding |
| `deepseek/deepseek-r1` | 64K | Top open reasoning model |
| `deepseek/deepseek-r1:free` | 64K | Free tier version |
| `deepseek/deepseek-v3:free` | 64K | Free tier version |

## Mistral Models

| Model ID | Context | Notes |
|----------|---------|-------|
| `mistralai/mistral-large` | 128K | Flagship Mistral |
| `mistralai/mistral-7b-instruct` | 32K | Small open model |
| `mistralai/mixtral-8x7b-instruct` | 32K | MoE model |

## Qwen Models

| Model ID | Context | Notes |
|----------|---------|-------|
| `qwen/qwen3-coder-480b` | 262K | Strongest free coding model |
| `qwen/qwen3-coder-480b:free` | 262K | Free tier |
| `qwen/qwen-2.5-72b-instruct` | 128K | Strong general model |

## Free Tier Models (as of June 2026)

OpenRouter offers 28+ free models. Free model IDs end with `:free`. No credit card required to use them.

| Model ID | Context | Strengths |
|----------|---------|-----------|
| `deepseek/deepseek-r1:free` | 64K | Reasoning, math |
| `deepseek/deepseek-v3:free` | 64K | General, coding |
| `meta-llama/llama-3.3-70b-instruct:free` | 128K | General purpose |
| `meta-llama/llama-4-scout:free` | 10M | Huge context |
| `qwen/qwen3-coder-480b:free` | 262K | Coding (strongest free) |
| `google/gemma-3-27b-it:free` | 8K | General |
| `google/gemini-flash-1.5:free` | 1M | Fast, multimodal |
| `microsoft/phi-3-medium-128k-instruct:free` | 128K | Small, efficient |

Find models with tool support + free tier:
```
https://openrouter.ai/models?supported_parameters=tools&order=top-weekly
```
Then filter by `:free`.

## Tool Calling Support

Many models support tool use / function calling. Check model details at:
```
https://openrouter.ai/models/{provider}/{model-name}
```

Or filter at: `https://openrouter.ai/models?supported_parameters=tools`

Models with confirmed tool calling support include:
- All Anthropic Claude models
- OpenAI GPT-4o, GPT-4o-mini, o3, o4-mini
- Google Gemini 2.5 Pro, Flash
- Meta Llama 3.3 70B Instruct, Llama 4 series
- DeepSeek Chat (V3), DeepSeek R1 (some variants)
- Qwen 2.5 series

## Programmatic Model Discovery

```python
import requests

response = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)
models = response.json()["data"]

for model in models:
    print(model["id"], model["context_length"])
```

## Model Deprecation

OpenRouter maintains backward compatibility with model aliases. When a model is deprecated, requests to the old ID are typically routed to the closest equivalent. Check the OpenRouter blog for deprecation notices.
