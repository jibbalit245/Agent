# Google Gemini API: Rate Limits

> Source: Fetched from GitHub google-gemini/cookbook and related sources (ai.google.dev/gemini-api/docs/rate-limits returned HTTP 403)
> Note: Rate limits vary by model and billing tier. Always verify at https://ai.google.dev/gemini-api/docs/rate-limits
> Date: 2026-06-20

## Overview

The Gemini API has rate limits that vary by model, billing tier, and service tier. Rate limits are primarily measured in:
- **RPM**: Requests per minute
- **TPM**: Tokens per minute
- **RPD**: Requests per day

## Free Tier Rate Limits

| Model | Requests/Min | Requests/Day |
|-------|-------------|-------------|
| `gemini-2.5-flash` | 15 RPM | Limited |
| `gemini-flash` models | 15 RPM | Limited |

- Not available in EEA, UK, CH without billing activation
- Rate limit increase requests available for higher quotas

## Priority Tier Rate Limits

Default rate limits for Priority tier are **0.3x the standard rate limit** for each model and tier.

Priority tier gracefully degrades to Standard instead of failing:
```python
# Detect if downgraded from Priority to Standard
tier = response.sdk_http_response.headers.get('x-gemini-service-tier')
if tier == "standard":
    print("Warning: Priority limit exceeded, processed at Standard tier.")
```

## Service Tier Impact

| Tier | Rate Limit Impact |
|------|------------------|
| Standard | Full rate limits |
| Flex | Full rate limits (but sheddable — may 503) |
| Priority | 0.3x standard rate limits (Tier 2 & 3 only) |
| Batch | High throughput, processed within 24 hours |

## Error Handling for Rate Limits

```python
from google.genai import errors
import time

def call_with_retry(prompt, max_retries=5, base_delay=1):
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
        except errors.APIError as e:
            if e.code == 429:  # Rate limit exceeded
                if attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)  # Exponential backoff
                    print(f"Rate limited, retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    raise
            else:
                raise
```

## Timeout Configuration

Configure timeouts to handle slow responses under load:

```python
from google import genai
from google.genai import types

# Global timeout (milliseconds)
client = genai.Client(
    api_key='YOUR_API_KEY',
    http_options=types.HttpOptions(timeout=120000)  # 2 minutes
)

# Per-request timeout (overrides global)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="Your prompt",
    config={
        "http_options": {"timeout": 30000}  # 30 seconds
    }
)
```

## Batch API for High Volume

For large volumes, use the Batch API (50% cheaper, no rate limit concerns):

```python
# Process millions of requests asynchronously
batch_job = client.batches.create(
    model="gemini-2.5-flash",
    src=inline_requests,  # or file-based
    config={'display_name': 'high-volume-job'}
)

# Results available within 24 hours
import time
while batch_job.state.name not in ('JOB_STATE_SUCCEEDED', 'JOB_STATE_FAILED'):
    time.sleep(30)
    batch_job = client.batches.get(name=batch_job.name)
```

## Checking Error Codes

```python
from google.genai import errors

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Your prompt'
    )
except errors.APIError as e:
    print(f"Error code: {e.code}")
    # 429 = Rate limit exceeded
    # 503 = Service unavailable (Flex tier shedding)
    # 403 = Forbidden
    # 404 = Model not found
    print(f"Error message: {e.message}")
```

## Async Concurrent Requests

For parallel processing within rate limits:

```python
import asyncio

async def process_batch(prompts, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_one(prompt):
        async with semaphore:
            return await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
    
    tasks = [process_one(p) for p in prompts]
    return await asyncio.gather(*tasks)

# Process 100 prompts with max 10 concurrent
results = asyncio.run(process_batch(my_prompts))
```

## Asynchronous Requests

```python
# Use async client for non-blocking requests
response = await client.aio.models.generate_content(
    model='gemini-2.5-flash',
    contents='Your prompt'
)

# Concurrent async operations
task1 = asyncio.create_task(client.aio.models.generate_content(...))
task2 = asyncio.create_task(client.aio.models.generate_content(...))
result1, result2 = await asyncio.gather(task1, task2)
```

## Rate Limit Increase

For production workloads requiring higher limits:
- Contact Google Cloud support for quota increases
- Consider Vertex AI for enterprise-grade limits
- Use Batch API for bulk non-time-sensitive workloads

## References

- Rate limits documentation: https://ai.google.dev/gemini-api/docs/rate-limits
- Pricing: https://ai.google.dev/pricing
- Priority inference: https://ai.google.dev/gemini-api/docs/priority-inference
- Flex inference: https://ai.google.dev/gemini-api/docs/flex-inference
