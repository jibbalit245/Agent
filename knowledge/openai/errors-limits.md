# OpenAI API Errors & Rate Limits
> Source: https://platform.openai.com/docs/guides/rate-limits
> Fetched: 2026-06-20

## Rate Limit Metrics

OpenAI tracks several metrics to enforce rate limits:

| Metric | Description |
|--------|-------------|
| **RPM** | Requests per minute |
| **RPD** | Requests per day |
| **TPM** | Tokens per minute |
| **TPD** | Tokens per day |
| **IPM** | Images per minute (for image models) |
| **Audio minutes** | For streaming audio models |

A request is blocked when **any** limit is hit, even if others are not. Example: sending 20 requests with 100 tokens each will hit a 20 RPM limit even if TPM is 150k and only 2k tokens were used.

Rate limits are enforced at the **organization level** and **project level**.

## Tier System

Tiers are automatically assigned based on API spend. Higher tiers get higher limits.

| Tier | Qualification | Notes |
|------|--------------|-------|
| **Free** | New account, no payment | Very low limits — for testing only |
| **Tier 1** | $5+ in payments | Entry-level; unlocked after first payment |
| **Tier 2** | $50+ in last 30 days | Moderate usage |
| **Tier 3** | $100+ in last 30 days | — |
| **Tier 4** | $250+ in last 30 days | — |
| **Tier 5** | $1,000+ in last 30 days | Highest standard limits |

Tier upgrades happen automatically. View current limits: https://platform.openai.com/account/limits

### Example Tier Limits (GPT-5 family, approximate)

| Model | Tier | TPM |
|-------|------|-----|
| `gpt-5` | Tier 1 | 500K |
| `gpt-5` | Tier 2 | 1M |
| `gpt-5` | Tier 3 | 2M |
| `gpt-5` | Tier 4 | 4M |
| `gpt-5-mini` | Tier 1 | 500K (5M batch) |

*Exact numbers vary by model and tier — check the limits page for current values.*

## Rate Limit Response Headers

When you make API requests, response headers tell you your current status:

```
x-ratelimit-limit-requests: 10000
x-ratelimit-limit-tokens: 2000000
x-ratelimit-remaining-requests: 9999
x-ratelimit-remaining-tokens: 1998500
x-ratelimit-reset-requests: 6ms
x-ratelimit-reset-tokens: 100ms
```

These help you implement proactive rate limiting in your code.

## Error Codes

### 429 — Rate Limit Error (Too Many Requests)

```json
{
  "error": {
    "message": "Rate limit reached for gpt-4o in organization org-xxx on tokens per min...",
    "type": "requests",
    "code": "rate_limit_exceeded"
  }
}
```

**Causes:**
- Too many requests per minute (RPM exceeded)
- Too many tokens per minute (TPM exceeded)
- Daily limits exhausted (RPD/TPD)
- Quota exceeded (billing limit hit — distinct from rate limits)

**Solution:** Back off and retry with exponential backoff (see below).

### 400 — Context Length Error

```json
{
  "error": {
    "message": "This model's maximum context length is 128000 tokens. However, your messages resulted in 130000 tokens.",
    "type": "invalid_request_error",
    "code": "context_length_exceeded"
  }
}
```

**This is NOT a rate limit error** — it's a per-request validation error. The input alone exceeds the model's context window.

**Solutions:**
- Truncate earlier messages in the conversation
- Summarize old conversation history
- Use a model with a larger context window (e.g., `gpt-4.1` with 1M tokens)
- Implement a sliding window over context

### Other Common Error Codes

| HTTP Status | Code | Meaning |
|-------------|------|---------|
| 400 | `invalid_request_error` | Bad request format, invalid parameters |
| 400 | `context_length_exceeded` | Input exceeds model's max context |
| 401 | `invalid_api_key` | API key is wrong, expired, or missing |
| 403 | `permission_denied` | Access denied to requested resource |
| 404 | `model_not_found` | Model ID doesn't exist or isn't accessible |
| 429 | `rate_limit_exceeded` | Too many requests or tokens |
| 429 | `insufficient_quota` | Billing quota/limit exceeded |
| 500 | `server_error` | OpenAI internal server error |
| 503 | `service_unavailable` | OpenAI is overloaded or down |

## Retry Strategy: Exponential Backoff with Jitter

The recommended approach for handling 429 errors:

```python
import time
import random
import openai
from openai import OpenAI

client = OpenAI()

def chat_with_retry(messages, model="gpt-4o", max_retries=6):
    """Make a chat completion with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages
            )
        except openai.RateLimitError as e:
            if attempt == max_retries - 1:
                raise  # give up after max retries
            # Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s + jitter
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limit hit. Waiting {wait_time:.2f}s before retry {attempt + 1}")
            time.sleep(wait_time)
        except openai.APIStatusError as e:
            if e.status_code == 500 or e.status_code == 503:
                # Server errors — also retry
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                raise  # don't retry client errors (400, 401, 404, etc.)
```

### Using the Official SDK's Built-in Retry

The OpenAI Python SDK has built-in retry logic:

```python
client = OpenAI(
    max_retries=3,  # default is 2
    timeout=30.0    # request timeout in seconds
)
```

Or per-request:
```python
response = client.with_options(max_retries=5).chat.completions.create(...)
```

## Handling Context Length Errors

```python
def truncate_messages(messages, max_tokens=100000, model="gpt-4o"):
    """Remove oldest messages when context is too long."""
    while True:
        try:
            # Try to estimate token count (use tiktoken for accuracy)
            return client.chat.completions.create(model=model, messages=messages)
        except openai.BadRequestError as e:
            if "context_length_exceeded" in str(e):
                # Remove the oldest non-system message
                for i, msg in enumerate(messages):
                    if msg["role"] != "system":
                        messages.pop(i)
                        break
            else:
                raise
```

## Proactive Rate Limit Management

### Token Counting with tiktoken

```python
import tiktoken

def count_tokens(messages, model="gpt-4o"):
    enc = tiktoken.encoding_for_model(model)
    total = 0
    for msg in messages:
        total += 4  # message overhead
        total += len(enc.encode(msg.get("content") or ""))
    total += 2  # reply priming
    return total
```

### Rate Limiting Your Own Code

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, rpm=500, tpm=100000):
        self.rpm = rpm
        self.tpm = tpm
        self.request_times = deque()
        self.token_counts = deque()
    
    def wait_if_needed(self, tokens_needed):
        now = time.time()
        minute_ago = now - 60
        
        # Clean old entries
        while self.request_times and self.request_times[0] < minute_ago:
            self.request_times.popleft()
        while self.token_counts and self.token_counts[0][0] < minute_ago:
            self.token_counts.popleft()
        
        # Check limits
        if len(self.request_times) >= self.rpm:
            sleep_time = 60 - (now - self.request_times[0])
            time.sleep(max(0, sleep_time))
        
        current_tpm = sum(t[1] for t in self.token_counts)
        if current_tpm + tokens_needed > self.tpm:
            sleep_time = 60 - (now - self.token_counts[0][0])
            time.sleep(max(0, sleep_time))
        
        self.request_times.append(time.time())
        self.token_counts.append((time.time(), tokens_needed))
```

## Increasing Rate Limits

1. **Automatically**: Spend more — tier upgrades happen automatically
2. **Apply for higher limits**: Contact OpenAI via the limits page
3. **Priority Processing**: Subscribe to priority processing add-on for higher throughput
4. **Scale Tier**: Reserved capacity for predictable high-volume usage

## Key Rules of Thumb

- Always implement exponential backoff for 429 errors
- Add random jitter to prevent thundering herd problems
- Check response headers to pre-emptively slow down
- Use `tiktoken` to count tokens before sending requests
- Cache responses when making repeated identical requests
- Use Batch API for workloads that tolerate 24h latency

## Sources
- [Rate limits | OpenAI API](https://platform.openai.com/docs/guides/rate-limits)
- [Error codes | OpenAI API](https://platform.openai.com/docs/guides/error-codes)
- [How to handle rate limits](https://cookbook.openai.com/examples/how_to_handle_rate_limits)
- [How can I solve 429: 'Too Many Requests' errors? | OpenAI Help Center](https://help.openai.com/en/articles/5955604-how-can-i-solve-429-too-many-requests-errors)
- [Priority processing | OpenAI API](https://developers.openai.com/api/docs/guides/priority-processing)
