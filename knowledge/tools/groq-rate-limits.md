# Groq Rate Limits

> **Fetch status:** HTTP 403 Forbidden from https://console.groq.com/docs/rate-limits — content below is from model training data (knowledge cutoff August 2025).

## Overview

Groq enforces rate limits per API key. Limits vary by:
- **Plan** (Free vs. paid)
- **Model**
- **Limit type** (requests per minute, tokens per minute, tokens per day)

---

## Rate Limit Types

| Abbreviation | Meaning |
|---|---|
| RPM | Requests Per Minute |
| RPD | Requests Per Day |
| TPM | Tokens Per Minute |
| TPD | Tokens Per Day |

---

## Free Tier Rate Limits (approximate, as of mid-2025)

### Llama Models

| Model | RPM | RPD | TPM | TPD |
|---|---|---|---|---|
| `llama-3.3-70b-versatile` | 30 | 14,400 | 6,000 | 500,000 |
| `llama-3.1-8b-instant` | 30 | 14,400 | 20,000 | 500,000 |
| `llama3-8b-8192` | 30 | 14,400 | 30,000 | 500,000 |
| `llama3-70b-8192` | 30 | 14,400 | 6,000 | 500,000 |

### Mixtral Models

| Model | RPM | RPD | TPM | TPD |
|---|---|---|---|---|
| `mixtral-8x7b-32768` | 30 | 14,400 | 5,000 | 500,000 |

### Gemma Models

| Model | RPM | RPD | TPM | TPD |
|---|---|---|---|---|
| `gemma-7b-it` | 30 | 14,400 | 15,000 | 500,000 |
| `gemma2-9b-it` | 30 | 14,400 | 15,000 | 500,000 |

### Whisper / Audio Models

| Model | RPM | RPD | Audio Seconds/Hour | Audio Seconds/Day |
|---|---|---|---|---|
| `whisper-large-v3` | 20 | 2,000 | 7,200 | 28,800 |
| `whisper-large-v3-turbo` | 20 | 2,000 | 7,200 | 28,800 |
| `distil-whisper-large-v3-en` | 20 | 2,000 | 7,200 | 28,800 |

---

## Rate Limit Headers

Every API response includes rate limit info in headers:

```
x-ratelimit-limit-requests: 30
x-ratelimit-limit-tokens: 6000
x-ratelimit-remaining-requests: 29
x-ratelimit-remaining-tokens: 5987
x-ratelimit-reset-requests: 2s
x-ratelimit-reset-tokens: 5s
```

---

## Handling Rate Limit Errors

When you exceed rate limits, Groq returns HTTP `429 Too Many Requests`:

```json
{
  "error": {
    "message": "Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_xxx` on tokens per minute. Limit: 6000, Used: 6000, Requested: 137.",
    "type": "tokens",
    "code": "rate_limit_exceeded"
  }
}
```

### Python Retry Example

```python
import time
from groq import Groq, RateLimitError

client = Groq()

def chat_with_retry(messages, model="llama-3.3-70b-versatile", max_retries=5):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
            )
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # exponential backoff
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

### Using tenacity

```python
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from groq import Groq, RateLimitError

client = Groq()

@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def create_completion(messages):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
    )
```

---

## Increasing Rate Limits

- **Contact Groq:** Submit a rate limit increase request at https://groq.com/
- **Upgrade plan:** Paid plans have higher or custom limits
- **Distribute across models:** Different models have independent rate limit pools

---

## Best Practices

1. **Track token usage:** Monitor `usage.total_tokens` in responses to stay within limits.
2. **Use streaming:** Streaming doesn't change rate limits but improves perceived latency.
3. **Implement exponential backoff:** Always retry with backoff on 429 errors.
4. **Cache responses:** Cache repeated queries to avoid unnecessary API calls.
5. **Batch efficiently:** Group multiple questions but respect token limits.
6. **Use smaller models for high-volume tasks:** `llama-3.1-8b-instant` has higher TPM limits.
