# Anthropic Messages API
> Source: https://docs.anthropic.com/en/api/messages
> Fetched: 2026-06-20

## Endpoint

```
POST https://api.anthropic.com/v1/messages
```

## Required Headers

```
x-api-key: sk-ant-api03-...
anthropic-version: 2023-06-01
content-type: application/json
```

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model ID, e.g. `claude-sonnet-4-6` |
| `messages` | array | Yes | Array of message objects |
| `max_tokens` | integer | Yes | Max tokens to generate (hard stop) |
| `system` | string or array | No | System prompt |
| `tools` | array | No | Tool definitions |
| `tool_choice` | object | No | Tool selection strategy |
| `stream` | boolean | No | Enable SSE streaming (default: false) |
| `temperature` | float | No | 0.0–1.0, default 1.0 |
| `top_p` | float | No | Nucleus sampling |
| `top_k` | integer | No | Top-k sampling |
| `stop_sequences` | array | No | Custom stop strings |
| `metadata` | object | No | `{"user_id": "..."}` for tracking |

## Message Format

Only `user` and `assistant` roles are supported (no `system` role in messages array):

```json
{
  "messages": [
    {"role": "user",      "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user",      "content": "How are you?"}
  ]
}
```

## Content Blocks

The `content` field can be a string or an array of content blocks:

### Text Block
```json
{"type": "text", "text": "Hello, world!"}
```

### Image Block (URL)
```json
{
  "type": "image",
  "source": {
    "type": "url",
    "url": "https://example.com/image.jpg"
  }
}
```

### Image Block (Base64)
```json
{
  "type": "image",
  "source": {
    "type": "base64",
    "media_type": "image/jpeg",
    "data": "/9j/4AAQSkZJRgAB..."
  }
}
```
Supported image formats: `image/jpeg`, `image/png`, `image/gif`, `image/webp`

### Tool Use Block (in assistant messages)
```json
{
  "type": "tool_use",
  "id": "toolu_01A09q90qw90lq917835lq9",
  "name": "get_weather",
  "input": {"location": "San Francisco, CA"}
}
```

### Tool Result Block (in user messages)
```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
  "content": "72°F, sunny",
  "is_error": false
}
```

## System Prompts

System prompts are set as a **separate parameter**, not inside the messages array:

```json
{
  "system": "You are a helpful assistant specializing in Python.",
  "messages": [...]
}
```

System can also be an array of content blocks (supports cache_control):
```json
{
  "system": [
    {
      "type": "text",
      "text": "You are a helpful assistant.",
      "cache_control": {"type": "ephemeral"}
    }
  ]
}
```

## Complete Basic Example

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.content[0].text)  # "The capital of France is Paris."
```

## Response Format

```json
{
  "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "text", "text": "The capital of France is Paris."}
  ],
  "model": "claude-sonnet-4-6",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 25,
    "output_tokens": 12,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0
  }
}
```

### stop_reason Values

| Value | Meaning |
|-------|---------|
| `end_turn` | Normal completion |
| `max_tokens` | Hit the `max_tokens` limit |
| `stop_sequence` | Hit a custom stop sequence |
| `tool_use` | Claude is calling a tool |

## Streaming

Enable with `stream: true`. Uses Server-Sent Events (SSE):

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a poem"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### SSE Event Types

```
event: message_start       # Full message metadata
event: content_block_start # New content block beginning
event: content_block_delta # Incremental text delta
event: content_block_stop  # Content block complete
event: message_delta       # Message-level updates (stop_reason, usage)
event: message_stop        # Stream complete
```

## Prompt Caching

Add `cache_control` to mark content for caching:

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "You are a helpful assistant with access to this large document: " + large_document,
            "cache_control": {"type": "ephemeral"}  # cache for 5 minutes (default)
        }
    ],
    messages=[{"role": "user", "content": "Summarize section 3"}]
)

# Check if cache was used
print(response.usage.cache_read_input_tokens)    # tokens read from cache
print(response.usage.cache_creation_input_tokens) # tokens written to cache
```

Cache TTL options: `"ephemeral"` (5 min default, or 1 hour with extended TTL flag).

## Multi-turn Conversations

```python
messages = []

while True:
    user_input = input("You: ")
    messages.append({"role": "user", "content": user_input})
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=messages
    )
    
    assistant_reply = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_reply})
    print(f"Claude: {assistant_reply}")
```

## Max Token Limits

| Model | Max Output Tokens |
|-------|------------------|
| Claude Fable 5 | 128,000 |
| Claude Opus 4.8 | 128,000 |
| Claude Sonnet 4.6 | 64,000 |
| Claude Haiku 4.5 | 64,000 |

Large outputs (>32K) typically require `stream: true` to avoid timeout errors.

## Common Errors

| Code | Error | Fix |
|------|-------|-----|
| 400 | `invalid_request_error` | Check required params (model, messages, max_tokens) |
| 401 | `authentication_error` | Invalid or missing `ANTHROPIC_API_KEY` |
| 403 | `permission_error` | Key lacks permission for this model |
| 429 | `rate_limit_error` | Slow down requests, implement backoff |
| 500 | `api_error` | Retry with exponential backoff |
| 529 | `overloaded_error` | Server overloaded, retry later |
