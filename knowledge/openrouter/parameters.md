# OpenRouter Request Parameters
> Source: https://openrouter.ai/docs/parameters
> Fetched: 2026-06-20
---

## Chat Completions Request Body

Full parameter reference for `POST https://openrouter.ai/api/v1/chat/completions`.

## Core Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `model` | string | Yes* | Model ID (e.g., `anthropic/claude-sonnet-4-6`) |
| `messages` | array | Yes | Conversation history |
| `max_tokens` | integer | No | Max output tokens (defaults vary by model) |
| `stream` | boolean | No | Enable SSE streaming (default: `false`) |

*Required unless using `models` array for multi-model routing.

## Message Format

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "Tell me a joke."}
  ]
}
```

Multi-modal content (images):
```json
{
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "What's in this image?"},
      {
        "type": "image_url",
        "image_url": {"url": "https://example.com/image.jpg"}
      }
    ]
  }]
}
```

## Sampling Parameters

| Parameter | Type | Range | Description |
|---|---|---|---|
| `temperature` | float | 0.0–2.0 | Randomness (higher = more creative) |
| `top_p` | float | 0.0–1.0 | Nucleus sampling (use instead of temperature, not both) |
| `top_k` | integer | ≥1 | Top-K sampling (not supported by all providers) |
| `frequency_penalty` | float | -2.0–2.0 | Penalize token frequency (reduces repetition) |
| `presence_penalty` | float | -2.0–2.0 | Penalize token presence (encourages topic diversity) |
| `repetition_penalty` | float | 0.0–2.0 | Alternative repetition penalty (>1.0 discourages repetition) |
| `min_p` | float | 0.0–1.0 | Minimum probability threshold |
| `top_a` | float | 0.0–1.0 | Top-A sampling |
| `seed` | integer | — | Random seed for reproducibility |

## Output Parameters

| Parameter | Type | Description |
|---|---|---|
| `stop` | string or string[] | Stop sequences (up to 4) |
| `logit_bias` | object | Token bias map `{token_id: bias}` (-100 to 100) |
| `logprobs` | boolean | Return log probabilities |
| `top_logprobs` | integer | Number of top log probabilities to return (1–20) |
| `response_format` | object | `{"type": "json_object"}` or `{"type": "text"}` |

## Tool / Function Calling Parameters

| Parameter | Type | Description |
|---|---|---|
| `tools` | array | Tool definitions (OpenAI format) |
| `tool_choice` | string or object | `"auto"`, `"none"`, `"required"`, or `{"type": "function", "function": {"name": "..."}}` |
| `parallel_tool_calls` | boolean | Allow parallel tool calls (default: `true`) |

Tool definition format:
```json
{
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get current weather for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {"type": "string", "description": "City name"},
          "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
        },
        "required": ["location"]
      }
    }
  }]
}
```

## OpenRouter-Specific Parameters

### `provider` Object

```json
{
  "provider": {
    "order": ["Anthropic", "AWS Bedrock"],
    "allow_fallbacks": true,
    "ignore": ["Together"],
    "sort": "price",
    "require_parameters": false,
    "data_collection": "deny",
    "quantizations": ["fp16", "bf16"],
    "context_length": 32768
  }
}
```

| Field | Type | Description |
|---|---|---|
| `order` | string[] | Preferred provider order |
| `allow_fallbacks` | boolean | Fall back to other providers if preferred fails |
| `ignore` | string[] | Providers to exclude |
| `sort` | string | Sort by `"price"`, `"latency"`, or `"throughput"` |
| `require_parameters` | boolean | Only providers supporting all requested params |
| `data_collection` | string | `"allow"` or `"deny"` (no-training providers only) |
| `quantizations` | string[] | Filter by quantization: `"int4"`, `"int8"`, `"fp8"`, `"fp16"`, `"bf16"`, `"unknown"` |
| `context_length` | integer | Minimum required context length |

### Multi-Model Arrays

```json
{
  "models": [
    "anthropic/claude-sonnet-4-6",
    "openai/gpt-4o"
  ]
}
```

Try each model in order — use the first one that succeeds.

### Fallback Models

```json
{
  "model": "anthropic/claude-opus-4-8",
  "fallbacks": [
    "anthropic/claude-sonnet-4-6",
    "openai/gpt-4o"
  ]
}
```

Triggered on non-client errors (e.g., rate limits, overload). Max 3 fallbacks.

### Structured Outputs

```json
{
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "calendar_event",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "date": {"type": "string"},
          "participants": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["name", "date", "participants"],
        "additionalProperties": false
      }
    }
  }
}
```

Only available on models that support structured outputs (OpenAI GPT-4o, claude-sonnet-4-6, etc.).

### Reasoning / Extended Thinking

Some models expose reasoning parameters:

```json
{
  "model": "openai/o3-mini",
  "reasoning_effort": "high"
}
```

For Anthropic models via OpenRouter, extended thinking is handled automatically per model capabilities.

## Stream Options

```json
{
  "stream": true,
  "stream_options": {
    "include_usage": true
  }
}
```

Include usage statistics in the final stream chunk.

## Full Example

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-or-v1-...",
    base_url="https://openrouter.ai/api/v1",
)

response = client.chat.completions.create(
    model="anthropic/claude-sonnet-4-6",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is quantum computing?"}
    ],
    max_tokens=1024,
    temperature=0.7,
    extra_body={
        "provider": {
            "order": ["Anthropic"],
            "data_collection": "deny"
        }
    }
)

print(response.choices[0].message.content)
```

Note: OpenRouter-specific parameters (`provider`, `models`, `fallbacks`) must be passed via `extra_body` when using the OpenAI SDK.
