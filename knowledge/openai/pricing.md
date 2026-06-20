# OpenAI API Pricing
> Source: https://openai.com/api/pricing
> Fetched: 2026-06-20

All prices are in **USD per 1 million tokens** unless noted otherwise. Prices are subject to change — verify at https://openai.com/api/pricing.

## Current Model Pricing (June 2026)

### GPT-4.1 Series

| Model | Input ($/1M) | Cached Input ($/1M) | Output ($/1M) |
|-------|-------------|---------------------|---------------|
| `gpt-4.1` | $2.00 | $0.50 | $8.00 |
| `gpt-4.1-mini` | ~$0.40 | ~$0.10 | ~$1.60 |
| `gpt-4.1-nano` | ~$0.10 | ~$0.025 | ~$0.40 |

### GPT-4o Series

| Model | Input ($/1M) | Cached Input ($/1M) | Output ($/1M) |
|-------|-------------|---------------------|---------------|
| `gpt-4o` | $2.50 | $1.25 | $10.00 |
| `gpt-4o-mini` | $0.150 | $0.075 | $0.600 |

### o-Series Reasoning Models

| Model | Input ($/1M) | Cached Input ($/1M) | Output ($/1M) |
|-------|-------------|---------------------|---------------|
| `o3` | $2.00 | — | $8.00 |
| `o4-mini` | $1.10 | — | $4.40 |
| `o3-mini` | ~$1.10 | — | ~$4.40 |
| `o1` | ~$15.00 | ~$7.50 | ~$60.00 |

### GPT-5 Series (2026)

| Model | Input ($/1M) | Output ($/1M) |
|-------|-------------|---------------|
| `gpt-5` | $1.25 | varies |
| `gpt-5-mini` | lower | lower |

*Check official pricing page for exact GPT-5 costs.*

## Batch API — 50% Discount

The **Batch API** processes requests asynchronously within 24 hours and costs 50% less than synchronous API calls.

```python
# Example: gpt-4o-mini batch pricing
# Standard: $0.150/1M input, $0.600/1M output
# Batch:    $0.075/1M input, $0.300/1M output
```

**How it works:**
1. Submit a `.jsonl` file with multiple requests
2. Requests are processed within 24 hours
3. Results returned as a `.jsonl` output file

**Best for:** Large-scale data processing, classification jobs, offline evaluation, bulk generation where latency doesn't matter.

**Limitations:** Not all models support Batch API. Pre-GPT-5 models have some caching limitations on Batch API.

```python
batch = client.batches.create(
    input_file_id=file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"
)
```

## Flex Processing

**Flex processing** is another cost-reduction option (also ~50% discount) for non-time-sensitive workloads. Unlike Batch API, Flex requests can still be made synchronously but with lower priority.

- Supports caching (Batch API has caching limitations for some models)
- Good alternative for o3, o4-mini when Batch caching isn't available

## Prompt Caching (Context Caching)

OpenAI automatically caches repeated prompt prefixes longer than **1,024 tokens**.

- Cached tokens are billed at a discounted rate (typically 50% of standard input price)
- Cache is maintained for recently used prompts
- Applied automatically — no configuration required
- Available on: GPT-4o, GPT-4o-mini, o1-preview, o1-mini, GPT-4.1, and fine-tuned versions

```json
// Response includes cache info in usage:
"usage": {
  "prompt_tokens": 1000,
  "prompt_tokens_details": {
    "cached_tokens": 800  // 800 tokens were cached (cheaper)
  }
}
```

**When to use**: System prompts, large context, RAG documents — any long repeated prefix. Structure prompts with static content first.

## Scale Tier (Reserved Capacity)

For predictable, high-volume workloads, OpenAI offers a **Scale Tier** with reserved throughput:

- `gpt-4.1` Scale Tier: $110/day per input unit (30k input tokens/min), $36/day per output unit (2.5k output tokens/min)
- Guarantees capacity even during peak demand

## Fine-Tuning

| Stage | Cost |
|-------|------|
| Training | Per-token cost during fine-tuning run |
| Inference | Higher per-token rate than base models |

Fine-tuned model IDs: `ft:gpt-4o-mini:org:name:id`

## Real-Time / Audio API

Audio tokens have separate pricing (per second of audio or per audio token). Check current pricing for:
- `gpt-4o-audio-preview` (audio input/output)
- `gpt-realtime` API

## Embeddings

| Model | Price ($/1M tokens) |
|-------|---------------------|
| `text-embedding-3-small` | $0.020 |
| `text-embedding-3-large` | $0.130 |
| `text-embedding-ada-002` | $0.100 |

## Image Generation (DALL-E)

Pricing is per image based on resolution and quality:
- DALL-E 3 standard 1024x1024: ~$0.040/image
- DALL-E 3 HD 1024x1024: ~$0.080/image

## Cost Optimization Strategies

1. **Use Batch API** for non-realtime workloads — 50% off
2. **Enable prompt caching** — repeat long prefixes to get cached rates
3. **Use smaller models** — GPT-4.1-nano or GPT-4o-mini for simpler tasks
4. **Limit max_tokens** — avoid generating unused tokens
5. **Use Flex processing** — for o3/o4-mini at reduced cost
6. **Monitor usage** at https://platform.openai.com/usage
7. **Set spending limits** in organization settings

## Sources
- [OpenAI API Pricing | OpenAI](https://openai.com/api/pricing/)
- [Pricing | OpenAI API](https://developers.openai.com/api/docs/pricing)
- [Prompt Caching in the API | OpenAI](https://openai.com/index/api-prompt-caching/)
- [Scale Tier for API Customers | OpenAI](https://openai.com/api-scale-tier/)
- [OpenAI API Pricing 2026: GPT-5 at $1.25/1M](https://pecollective.com/tools/openai-api-pricing/)
