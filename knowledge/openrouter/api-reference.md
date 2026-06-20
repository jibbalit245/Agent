# OpenRouter API Reference
> Source: https://openrouter.ai/docs/api-reference, https://openrouter.ai/docs/provider-routing
> Fetched: 2026-06-20

## Base URL

```
https://openrouter.ai/api/v1
```

## Authentication

All requests require a Bearer token:
```
Authorization: Bearer sk-or-v1-...
```

## Required Headers

```http
Authorization: Bearer sk-or-v1-...     # Required — your OpenRouter API key
Content-Type: application/json          # Required for POST requests
HTTP-Referer: https://yourapp.com       # Optional — app URL for analytics/leaderboards
X-Title: My Application Name           # Optional — app name for analytics/leaderboards
```

The `HTTP-Referer` and `X-Title` headers are optional but recommended for attribution and appearing on OpenRouter leaderboards.

## Primary Endpoint

### Chat Completions

```
POST https://openrouter.ai/api/v1/chat/completions
```

Fully compatible with OpenAI's `/v1/chat/completions` format.

#### Request Body

```json
{
  "model": "anthropic/claude-sonnet-4-6",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user",   "content": "What is 2+2?"}
  ],
  "max_tokens": 512,
  "temperature": 0.7,
  "stream": false
}
```

#### Core Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Model ID (e.g., `anthropic/claude-sonnet-4-6`) |
| `messages` | array | Array of `{role, content}` objects |
| `max_tokens` | integer | Maximum output tokens |
| `temperature` | float | 0.0–2.0, controls randomness |
| `stream` | boolean | Enable SSE streaming |
| `top_p` | float | Nucleus sampling |
| `stop` | string/array | Stop sequences |
| `tools` | array | Tool/function definitions (OpenAI format) |
| `tool_choice` | string/object | Tool selection strategy |

#### OpenRouter-Specific Parameters

```json
{
  "model": "anthropic/claude-sonnet-4-6",
  "messages": [...],
  
  "provider": {
    "order": ["Anthropic", "AWS Bedrock"],
    "allow_fallbacks": true,
    "data_collection": "deny"
  },
  
  "models": [
    "anthropic/claude-sonnet-4-6",
    "openai/gpt-4o"
  ],
  
  "fallbacks": [
    "anthropic/claude-haiku-4-5",
    "openai/gpt-4o-mini"
  ]
}
```

## Response Format

```json
{
  "id": "gen-1234567890",
  "object": "chat.completion",
  "created": 1719849600,
  "model": "anthropic/claude-sonnet-4-6",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "4"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 28,
    "completion_tokens": 1,
    "total_tokens": 29
  }
}
```

The generation ID is also returned in the `X-Generation-Id` response header for debugging.

## Streaming

Set `stream: true` to enable Server-Sent Events (SSE):

```python
import requests

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "anthropic/claude-sonnet-4-6",
        "messages": [{"role": "user", "content": "Count to 10"}],
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line.startswith(b"data: "):
        data = line[6:]
        if data != b"[DONE]":
            import json
            chunk = json.loads(data)
            delta = chunk["choices"][0]["delta"].get("content", "")
            print(delta, end="", flush=True)
```

Streaming errors that occur before any tokens are sent use standard HTTP error codes. Errors mid-stream are sent as SSE error events.

## Provider Routing

Control which underlying providers serve your request:

```json
{
  "model": "anthropic/claude-sonnet-4-6",
  "provider": {
    "order": ["Anthropic", "AWS Bedrock", "Google Vertex"],
    "allow_fallbacks": true,
    "data_collection": "deny",
    "quantizations": ["fp16", "bf16"]
  }
}
```

### Provider Options

| Option | Values | Description |
|--------|--------|-------------|
| `order` | list of provider names | Try these providers in order |
| `allow_fallbacks` | true/false | Fall back to other providers on failure |
| `data_collection` | `"deny"` / `"allow"` | Prevent/allow provider data retention |
| `quantizations` | list | Filter by model quantization |

## Fallback Models

Specify fallback models to try if the primary model fails:

```json
{
  "model": "anthropic/claude-opus-4-8",
  "fallbacks": [
    "anthropic/claude-sonnet-4-6",
    "openai/gpt-4o"
  ]
}
```

Fallbacks trigger on:
- Provider rate limits (429)
- Provider downtime (5xx errors)
- Moderation refusals
- Context length exceeded

## Multi-Model Routing

Send a request that OpenRouter routes to the best available model:

```json
{
  "models": [
    "anthropic/claude-sonnet-4-6",
    "openai/gpt-4o",
    "google/gemini-2.5-pro"
  ],
  "route": "fallback"
}
```

## Tool Use / Function Calling

Uses OpenAI's tool format:

```json
{
  "model": "anthropic/claude-sonnet-4-6",
  "messages": [{"role": "user", "content": "What's the weather?"}],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string"}
          },
          "required": ["location"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

## Error Codes

| HTTP Code | Error Type | Description | Action |
|-----------|-----------|-------------|--------|
| 400 | `bad_request` | Invalid parameters or malformed request | Fix request |
| 401 | `invalid_api_key` | Bad or missing API key | Check `OPENROUTER_API_KEY` |
| 402 | `insufficient_credits` | Not enough credits | Add credits at openrouter.ai |
| 403 | `moderation` | Content flagged by provider moderation | Modify prompt |
| 408 | `timeout` | Request timed out | Retry, or use smaller max_tokens |
| 429 | `rate_limit_exceeded` | Too many requests | Backoff and retry |
| 500 | `server_error` | Internal server error | Retry |
| 502/503 | `provider_error` | Upstream provider unavailable | Retry or use fallback |

### Error Response Format

```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded",
    "type": "rate_limit_exceeded",
    "metadata": {
      "provider": "anthropic",
      "raw": "Too many requests"
    }
  }
}
```

## Other Endpoints

### List Models

```
GET https://openrouter.ai/api/v1/models
Authorization: Bearer sk-or-v1-...
```

Returns all available models with pricing, context windows, and capabilities.

### Get Generation Details

```
GET https://openrouter.ai/api/v1/generation?id={generation_id}
Authorization: Bearer sk-or-v1-...
```

Get cost and metadata for a completed generation by its ID.

### Check Credits

```
GET https://openrouter.ai/api/v1/auth/key
Authorization: Bearer sk-or-v1-...
```

Returns your current credit balance and usage stats.

## Common Integration Patterns

### Drop-in OpenAI replacement

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-or-v1-...",
    base_url="https://openrouter.ai/api/v1"
)

# All existing OpenAI code works — just change model ID format
response = client.chat.completions.create(
    model="anthropic/claude-sonnet-4-6",  # instead of "claude-sonnet-4-6"
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Retry with backoff on 429

```python
import time
import requests

def call_with_retry(payload, max_retries=3):
    for attempt in range(max_retries):
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload
        )
        if resp.status_code == 429:
            wait = 2 ** attempt
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise Exception("Max retries exceeded")
```
