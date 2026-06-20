# Rate Limits
> Source: https://platform.claude.com/docs/en/api/rate-limits.md
> Fetched: 2026-06-20
---

## Overview

Claude API rate limits are enforced per workspace and reset on a rolling basis. Limits apply to both requests per minute (RPM) and tokens per minute (TPM/ITPM/OTPM).

## Limit Types

| Acronym | Meaning |
|---|---|
| RPM | Requests per minute |
| TPM | Tokens per minute (input + output combined) |
| ITPM | Input tokens per minute |
| OTPM | Output tokens per minute |

## Rate Limit Tiers

Limits scale with your spend tier (1–5). Starting tier is based on account age and usage history.

### Tier 1 (New Accounts)

| Model | RPM | ITPM | OTPM |
|---|---|---|---|
| Claude Opus 4.8 | 50 | 40,000 | 16,000 |
| Claude Sonnet 4.6 | 50 | 40,000 | 16,000 |
| Claude Haiku 4.5 | 50 | 50,000 | 10,000 |

### Tier 2

| Model | RPM | ITPM | OTPM |
|---|---|---|---|
| Claude Opus 4.8 | 1,000 | 200,000 | 80,000 |
| Claude Sonnet 4.6 | 1,000 | 200,000 | 80,000 |
| Claude Haiku 4.5 | 1,000 | 200,000 | 80,000 |

### Tier 3

| Model | RPM | ITPM | OTPM |
|---|---|---|---|
| Claude Opus 4.8 | 2,000 | 400,000 | 160,000 |
| Claude Sonnet 4.6 | 2,000 | 400,000 | 160,000 |
| Claude Haiku 4.5 | 2,000 | 400,000 | 160,000 |

### Tier 4

| Model | RPM | ITPM | OTPM |
|---|---|---|---|
| Claude Opus 4.8 | 4,000 | 800,000 | 320,000 |
| Claude Sonnet 4.6 | 4,000 | 800,000 | 320,000 |
| Claude Haiku 4.5 | 4,000 | 800,000 | 320,000 |

### Tier 5

Enterprise-level limits — contact Anthropic Sales.

## Rate Limit Headers

Every API response includes rate limit headers:

```http
anthropic-ratelimit-requests-limit: 1000
anthropic-ratelimit-requests-remaining: 999
anthropic-ratelimit-requests-reset: 2024-01-01T00:00:00Z

anthropic-ratelimit-input-tokens-limit: 200000
anthropic-ratelimit-input-tokens-remaining: 199975
anthropic-ratelimit-input-tokens-reset: 2024-01-01T00:00:30Z

anthropic-ratelimit-output-tokens-limit: 80000
anthropic-ratelimit-output-tokens-remaining: 79950
anthropic-ratelimit-output-tokens-reset: 2024-01-01T00:00:30Z

retry-after: 30  # only present on 429 responses
```

## Rate Limit Error

HTTP `429 Too Many Requests`:

```json
{
  "type": "error",
  "error": {
    "type": "rate_limit_error",
    "message": "Number of request tokens has exceeded your per-minute rate limit (https://platform.anthropic.com/docs/en/api/rate-limits)"
  }
}
```

## Handling Rate Limits

The SDK auto-retries 429 errors with exponential backoff (default: 2 retries):

```python
# SDK auto-retry is enabled by default
client = anthropic.Anthropic(max_retries=5)  # increase retries
```

### Custom Retry Logic

```python
import anthropic
import time

client = anthropic.Anthropic(max_retries=0)  # disable auto-retry for custom handling

def call_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.messages.create(
                model="claude-opus-4-8",
                max_tokens=1024,
                messages=messages,
            )
        except anthropic.RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            # Get retry delay from header
            retry_after = int(e.response.headers.get("retry-after", "60"))
            print(f"Rate limited. Waiting {retry_after}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_after)
```

### Proactive Rate Limit Monitoring

```python
def make_request_with_monitoring(messages):
    response = client.messages.with_raw_response.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=messages,
    )
    
    # Log rate limit state
    remaining_requests = response.headers.get("anthropic-ratelimit-requests-remaining")
    remaining_input = response.headers.get("anthropic-ratelimit-input-tokens-remaining")
    
    if int(remaining_requests or 999) < 10:
        print(f"WARNING: Only {remaining_requests} requests remaining this minute")
    
    return response.parse()
```

## Batch API for High-Volume Workloads

For rate-limit-sensitive workloads, use the Message Batches API:

- **50% cost reduction** on all token usage
- **No rate limit** — batches process asynchronously
- Up to 100,000 requests or 256 MB per batch
- Results available within 1 hour (max 24 hours)

```python
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

batch = client.messages.batches.create(
    requests=[
        Request(
            custom_id=f"request-{i}",
            params=MessageCreateParamsNonStreaming(
                model="claude-opus-4-8",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
        )
        for i, prompt in enumerate(prompts)
    ]
)
```

## Context Window Limits

These are not rate limits but hard limits per request:

| Model | Max Input (context window) | Max Output |
|---|---|---|
| Claude Opus 4.8 | 1,000,000 tokens | 32,000 tokens |
| Claude Sonnet 4.6 | 1,000,000 tokens | 64,000 tokens |
| Claude Haiku 4.5 | 200,000 tokens | 8,192 tokens |

Exceeding these returns `400 Bad Request`, not `429`.

## Increasing Limits

1. Usage automatically increases tier as spend increases
2. Contact Anthropic for enterprise/high-volume plans
3. Use prompt caching to reduce token consumption
4. Use batch API for non-time-sensitive workloads

## Checking Current Limits

View your current tier and limits in the [Anthropic Console](https://console.anthropic.com) under **Settings** → **Rate Limits**.
