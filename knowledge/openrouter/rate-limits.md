# OpenRouter Rate Limits
> Source: https://openrouter.ai/docs/limits
> Fetched: 2026-06-20
---

## Overview

OpenRouter enforces rate limits at multiple levels: platform-wide, per-model, and per-key. Limits depend on your account tier.

## Free Tier Limits

Accounts without a payment method added:

| Limit | Value |
|---|---|
| Requests per minute | 20 |
| Requests per day | 200 |
| Models available | Free models only (`:free` suffix) |
| Context limit | Model-dependent (usually lower) |

Free models use the `:free` suffix: `meta-llama/llama-3.3-70b-instruct:free`

## Paid Tier Limits

Accounts with a payment method or existing credits:

| Limit | Default Value |
|---|---|
| Requests per minute | 200–1000 (varies by model and load) |
| Requests per day | Effectively unlimited for most models |
| Tokens per minute | Model-dependent |
| Tokens per day | Model-dependent |

Limits are enforced per-model and can vary based on provider capacity.

## Per-Key Limits

Set custom limits per API key in the dashboard:

- **Credit limit**: maximum spend per key (in USD credits)
- **Rate limit**: maximum requests per interval

## Checking Your Limits

```bash
curl https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer sk-or-v1-..."
```

Response includes:
```json
{
  "data": {
    "usage": 1234,
    "limit": null,
    "rate_limit": {
      "requests": 200,
      "interval": "10s"
    }
  }
}
```

## Rate Limit Headers

OpenRouter returns standard rate limit headers:

```http
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 195
X-RateLimit-Reset: 1719849660
```

## Error Response on Rate Limit

```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded. Please retry after 10 seconds.",
    "metadata": {
      "retry_after": 10
    }
  }
}
```

HTTP status: `429 Too Many Requests`

## Handling Rate Limits

```python
import time
import openai

client = openai.OpenAI(
    api_key="sk-or-v1-...",
    base_url="https://openrouter.ai/api/v1",
)

def call_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model="anthropic/claude-sonnet-4-6",
                messages=messages,
            )
        except openai.RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            retry_after = int(e.response.headers.get("retry-after", "10"))
            time.sleep(retry_after)
```

## Increasing Limits

- Add credits to your account to access higher rate limits
- Contact OpenRouter support for enterprise/high-volume plans
- Use fallback models to route around per-model limits
- Distribute load across multiple API keys

## Model-Specific Limits

Some models have tighter constraints due to provider capacity:

- High-demand models (e.g., `anthropic/claude-opus-4-8`) may have lower per-minute limits
- Open-source models hosted by multiple providers generally have higher aggregate capacity
- Use `provider.sort: "throughput"` to route to highest-capacity providers

## Context Window Limits

| Model | Context Window |
|---|---|
| `anthropic/claude-sonnet-4-6` | 1M tokens |
| `anthropic/claude-opus-4-8` | 1M tokens |
| `anthropic/claude-haiku-4-5` | 200K tokens |
| `openai/gpt-4o` | 128K tokens |
| `openai/o3-mini` | 200K tokens |
| `meta-llama/llama-3.3-70b-instruct` | 131K tokens |
| `google/gemini-2.5-pro` | 1M tokens |

Context limits are enforced by the underlying provider.
