# OpenRouter Error Codes
> Source: https://openrouter.ai/docs/errors
> Fetched: 2026-06-20
---

## Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": 400,
    "message": "Description of the error",
    "metadata": {
      "provider_name": "Anthropic",
      "raw": "{\"type\":\"error\",\"error\":{...}}"
    }
  }
}
```

The `metadata.raw` field contains the raw error from the upstream provider when available.

## HTTP Status Codes

| Status | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad Request — invalid parameters |
| 401 | Unauthorized — invalid or missing API key |
| 402 | Payment Required — insufficient credits |
| 403 | Forbidden — API key lacks permission |
| 408 | Request Timeout — model took too long |
| 429 | Too Many Requests — rate limit exceeded |
| 502 | Bad Gateway — upstream provider error |
| 503 | Service Unavailable — model/provider unavailable |

## Common Errors

### 400 Bad Request

```json
{
  "error": {
    "code": 400,
    "message": "Invalid model: anthropic/claude-nonexistent. Check available models at /api/v1/models"
  }
}
```

Causes:
- Invalid model ID
- Malformed request body
- Invalid parameter values
- Missing required fields

### 401 Unauthorized

```json
{
  "error": {
    "code": 401,
    "message": "No auth credentials found. Please add an API key or use OAuth."
  }
}
```

Causes:
- Missing `Authorization` header
- Invalid API key format (must start with `sk-or-v1-`)
- Expired or revoked key

### 402 Payment Required

```json
{
  "error": {
    "code": 402,
    "message": "Insufficient credits. Add credits at https://openrouter.ai/credits"
  }
}
```

Causes:
- No credits remaining
- Per-key credit limit reached
- Model requires paid account (not available on free tier)

### 429 Too Many Requests

```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded. Retry after 10 seconds.",
    "metadata": {
      "retry_after": 10
    }
  }
}
```

Causes:
- Exceeding requests-per-minute limit
- Exceeding requests-per-day limit (free tier)
- Model-specific rate limit hit

### 502 Bad Gateway

```json
{
  "error": {
    "code": 502,
    "message": "The upstream provider returned an error.",
    "metadata": {
      "provider_name": "Anthropic",
      "raw": "{\"type\":\"error\",\"error\":{\"type\":\"overloaded_error\",\"message\":\"Overloaded\"}}"
    }
  }
}
```

Causes:
- Upstream provider (Anthropic, OpenAI, etc.) returned an error
- Provider is overloaded
- Provider API outage

Strategy: Enable `provider.allow_fallbacks: true` and configure `fallbacks` to handle these automatically.

### 503 Service Unavailable

```json
{
  "error": {
    "code": 503,
    "message": "This model is currently unavailable. Try again later or use a different model."
  }
}
```

Causes:
- Model temporarily pulled from availability
- All providers for this model are at capacity

## Provider-Specific Errors in Metadata

When a provider returns an error, it appears in `metadata.raw`:

**Anthropic errors:**
```json
{
  "type": "error",
  "error": {
    "type": "overloaded_error",
    "message": "Overloaded"
  }
}
```

**OpenAI errors:**
```json
{
  "error": {
    "message": "That model is currently overloaded with other requests.",
    "type": "server_error",
    "code": "server_error"
  }
}
```

## Error Handling Pattern

```python
import openai
import time

client = openai.OpenAI(
    api_key="sk-or-v1-...",
    base_url="https://openrouter.ai/api/v1",
)

def safe_completion(messages, model="anthropic/claude-sonnet-4-6"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content
        
    except openai.AuthenticationError:
        raise RuntimeError("Invalid API key")
        
    except openai.PermissionDeniedError as e:
        if "credits" in str(e).lower():
            raise RuntimeError("Insufficient credits — add at openrouter.ai/credits")
        raise
        
    except openai.RateLimitError as e:
        retry_after = int(getattr(e.response, "headers", {}).get("retry-after", 10))
        print(f"Rate limited. Waiting {retry_after}s...")
        time.sleep(retry_after)
        return safe_completion(messages, model)  # retry
        
    except openai.BadRequestError as e:
        raise RuntimeError(f"Invalid request: {e.message}")
        
    except openai.APIStatusError as e:
        if e.status_code in (502, 503):
            # Provider error — try fallback or wait
            raise RuntimeError(f"Provider error: {e.message}")
        raise
```

## Streaming Errors

Errors during streaming appear as a special event:

```
data: {"error": {"code": 502, "message": "Provider overloaded"}}
```

Always check for `error` key in stream chunks before accessing `choices`.

## Using Fallbacks to Handle Errors

Configure automatic fallbacks to handle 502/503 errors:

```json
{
  "model": "anthropic/claude-opus-4-8",
  "fallbacks": [
    "anthropic/claude-sonnet-4-6",
    "openai/gpt-4o"
  ],
  "provider": {
    "allow_fallbacks": true
  }
}
```

OpenRouter automatically retries with fallback models on non-client errors.
