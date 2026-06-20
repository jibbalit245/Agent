# Google Gemini API: Pricing

> Source: Fetched from GitHub google-gemini/cookbook and related sources (ai.google.dev/pricing returned HTTP 403)
> Note: Pricing changes frequently. Always verify at https://ai.google.dev/pricing
> Date: 2026-06-20

## Overview

The Gemini API uses a token-based pricing model. Key factors:
- Input tokens (prompt + context)
- Output tokens (generated response)
- Cached content tokens (discounted)
- Special media (images, video, audio) converted to tokens

## Free Tier

- Available for Gemini Flash models
- **Rate limit**: 15 requests per minute
- Not available in EEA, UK, CH without billing activation
- No credit card required to start

## Service Tier Pricing Multipliers

| Tier | Cost Multiplier | Latency | Best For |
|------|----------------|---------|----------|
| Standard | 1x (base price) | Seconds-minutes | General workflows |
| Flex | 0.5x (50% discount) | 1-15 min target | Background tasks, non-urgent |
| Priority | 1.75x-2x (+75-100%) | Milliseconds | Production, user-facing |
| Batch | 0.5x (50% discount) | Up to 24 hours | Massive datasets |
| Context Cache | ~0.1x (~90% discount) | Faster first token | Repeated large contexts |

## Context Caching Pricing

Cached tokens are discounted significantly (~90% off standard input price). Storage has a recurring cost while cache is active.

```python
# Example token breakdown for a cached request
response.usage_metadata.cached_content_token_count  # Cheap
response.usage_metadata.prompt_token_count           # New tokens at full price
response.usage_metadata.candidates_token_count       # Output at full price
```

## Image Generation Pricing

The Imagen 4 models require active billing — not available on free tier.

| Model | Notes |
|-------|-------|
| `imagen-4.0-generate-001` | Standard quality |
| `imagen-4.0-ultra-generate-001` | Highest quality, 1 image/request |
| `imagen-4.0-fast-generate-001` | Lower cost, faster |

## Batch API Pricing

- **50% discount** vs standard pricing
- Process millions of requests asynchronously
- Results within 24-hour SLO

```python
# Create a batch job at 50% discount
batch_job = client.batches.create(
    model="gemini-2.5-flash",
    src=inline_requests,
    config={'display_name': 'cost-efficient-batch'}
)
```

## Token Counting for Cost Estimation

Always count tokens before making requests to estimate costs:

```python
from google import genai

client = genai.Client(api_key='YOUR_API_KEY')

token_response = client.models.count_tokens(
    model='gemini-2.5-flash',
    contents='Your prompt here'
)

print(f"Estimated prompt tokens: {token_response.total_tokens}")
```

Token equivalencies:
- 1 token ≈ 4 characters
- 100 tokens ≈ 60-80 English words

## Usage Metadata (Track Actual Usage)

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Your prompt'
)

meta = response.usage_metadata
print(f"Prompt tokens:    {meta.prompt_token_count}")
print(f"Output tokens:    {meta.candidates_token_count}")
print(f"Thinking tokens:  {meta.thoughts_token_count}")
print(f"Cached tokens:    {meta.cached_content_token_count}")
print(f"Total tokens:     {meta.total_token_count}")
```

## Priority Tier

```python
# Use priority tier for production workloads
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="Your prompt here",
    config={'service_tier': 'priority'},
)

# Verify which tier was actually used
tier = response.sdk_http_response.headers.get('x-gemini-service-tier')
```

Priority tier notes:
- Default rate limits: 0.3x the standard rate limit
- Available on Tier 2 & 3 only (paid plans)
- Gracefully downgrades to standard if limit exceeded

## Flex Tier

```python
# Use flex tier for background/non-urgent work
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="Your prompt here",
    config={
        'service_tier': 'flex',
        'http_options': {'timeout': 900000}  # 15 min timeout in ms
    },
)
```

Flex tier notes:
- "Sheddable" compute — may fail with 503 during high load
- Implement retry with exponential backoff:

```python
import time
from google.genai import errors

def call_with_retry(max_retries=3, base_delay=5):
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model='gemini-2.5-flash',
                contents="Your prompt",
                config={"service_tier": "flex"},
            )
        except errors.APIError as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2**attempt)  # Exponential backoff
                time.sleep(delay)
            else:
                # Fall back to standard tier
                return client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents="Your prompt",
                )
```

## Current Pricing Reference

For up-to-date pricing, always check: **https://ai.google.dev/pricing**

Key variables in pricing:
- Model tier (Flash vs Pro)
- Input token count
- Output token count
- Whether context caching is used
- Service tier (Standard/Flex/Priority/Batch)
- Region availability
