# Groq API Reference

> **Fetch status:** HTTP 403 Forbidden from https://console.groq.com/docs/api-reference — content below is from model training data (knowledge cutoff August 2025).

## Base URL

```
https://api.groq.com/openai/v1
```

## Authentication

All requests must include an `Authorization` header:

```
Authorization: Bearer gsk_your_api_key_here
```

---

## Endpoints

### POST /chat/completions

Create a chat completion.

**Request Body:**

```json
{
  "model": "llama-3.3-70b-versatile",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello!"
    }
  ],
  "temperature": 1.0,
  "max_tokens": 1024,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "stop": null,
  "stream": false,
  "n": 1,
  "seed": null,
  "response_format": {"type": "text"},
  "tools": null,
  "tool_choice": "auto",
  "parallel_tool_calls": true,
  "user": null,
  "logprobs": false,
  "top_logprobs": null
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | string | Yes | — | Model ID |
| `messages` | array | Yes | — | List of message objects |
| `temperature` | float | No | 1.0 | Sampling temperature (0.0–2.0) |
| `max_tokens` | integer | No | model max | Maximum tokens to generate |
| `top_p` | float | No | 1.0 | Nucleus sampling probability |
| `frequency_penalty` | float | No | 0.0 | Frequency penalty (-2.0–2.0) |
| `presence_penalty` | float | No | 0.0 | Presence penalty (-2.0–2.0) |
| `stop` | string/array | No | null | Stop sequences |
| `stream` | boolean | No | false | Stream partial results |
| `n` | integer | No | 1 | Number of completions |
| `seed` | integer | No | null | Random seed for reproducibility |
| `response_format` | object | No | `{"type":"text"}` | `text` or `json_object` |
| `tools` | array | No | null | Tool/function definitions |
| `tool_choice` | string/object | No | `"auto"` | How to use tools |
| `parallel_tool_calls` | boolean | No | true | Allow parallel tool calls |
| `user` | string | No | null | End-user identifier |
| `logprobs` | boolean | No | false | Return log probabilities |
| `top_logprobs` | integer | No | null | Number of top logprobs (1–20) |

**Message Object:**

```json
{
  "role": "user",          // "system" | "user" | "assistant" | "tool"
  "content": "Hello",
  "name": null,            // Optional name
  "tool_calls": null,      // For assistant messages with tool calls
  "tool_call_id": null     // For tool result messages
}
```

**Response:**

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1719000000,
  "model": "llama-3.3-70b-versatile",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?",
        "tool_calls": null
      },
      "finish_reason": "stop",
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30,
    "prompt_time": 0.01,
    "completion_time": 0.05,
    "total_time": 0.06
  },
  "system_fingerprint": "fp_abc123",
  "x_groq": {
    "id": "req_abc123"
  }
}
```

**Streaming Response (SSE):**

```
data: {"id":"chatcmpl-abc","object":"chat.completion.chunk","created":1719000000,"model":"llama-3.3-70b-versatile","choices":[{"index":0,"delta":{"role":"assistant","content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc","object":"chat.completion.chunk","created":1719000000,"model":"llama-3.3-70b-versatile","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc","object":"chat.completion.chunk","created":1719000000,"model":"llama-3.3-70b-versatile","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"x_groq":{"usage":{"prompt_tokens":20,"completion_tokens":2,"total_tokens":22}}}

data: [DONE]
```

---

### GET /models

List all available models.

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "llama-3.3-70b-versatile",
      "object": "model",
      "created": 1693721698,
      "owned_by": "Meta",
      "active": true,
      "context_window": 128000,
      "public_apps": null
    },
    ...
  ]
}
```

---

### GET /models/{model_id}

Retrieve a specific model.

**Response:**

```json
{
  "id": "llama-3.3-70b-versatile",
  "object": "model",
  "created": 1693721698,
  "owned_by": "Meta",
  "active": true,
  "context_window": 128000
}
```

---

### POST /audio/transcriptions

Transcribe audio to text.

**Request (multipart/form-data):**

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | file | Yes | Audio file (mp3, mp4, mpeg, mpga, m4a, wav, webm) |
| `model` | string | Yes | `whisper-large-v3`, `whisper-large-v3-turbo`, `distil-whisper-large-v3-en` |
| `language` | string | No | ISO 639-1 language code |
| `prompt` | string | No | Context/vocabulary hints |
| `response_format` | string | No | `json`, `text`, `srt`, `verbose_json`, `vtt` |
| `temperature` | float | No | 0.0–1.0 |

```python
with open("audio.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        file=("audio.mp3", audio_file, "audio/mpeg"),
        model="whisper-large-v3",
        language="en",
        response_format="text",
    )
print(transcription)
```

```bash
curl -X POST https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F "file=@audio.mp3" \
  -F "model=whisper-large-v3" \
  -F "response_format=text"
```

---

### POST /audio/translations

Translate audio to English text.

**Request:** Same as `/audio/transcriptions` (no `language` parameter needed).

---

## Error Codes

| HTTP Status | Error Type | Description |
|---|---|---|
| 400 | `invalid_request_error` | Bad request / invalid parameters |
| 401 | `authentication_error` | Invalid or missing API key |
| 403 | `permission_denied_error` | Not authorized for this resource |
| 404 | `not_found_error` | Model or resource not found |
| 422 | `unprocessable_entity_error` | Semantic validation error |
| 429 | `rate_limit_error` | Too many requests |
| 500 | `api_error` | Internal server error |
| 503 | `service_unavailable_error` | Service temporarily unavailable |

**Error Response Format:**

```json
{
  "error": {
    "message": "Rate limit reached for model `llama-3.3-70b-versatile`...",
    "type": "tokens",
    "code": "rate_limit_exceeded"
  }
}
```

---

## Rate Limit Headers

```
x-ratelimit-limit-requests: 30
x-ratelimit-limit-tokens: 6000
x-ratelimit-remaining-requests: 29
x-ratelimit-remaining-tokens: 5987
x-ratelimit-reset-requests: 2s
x-ratelimit-reset-tokens: 5.123s
retry-after: 5
```

---

## SDK Clients

### Python

```bash
pip install groq
```

```python
from groq import Groq, AsyncGroq

# Sync
client = Groq(api_key="gsk_...")

# Async
client = AsyncGroq(api_key="gsk_...")
```

### JavaScript / TypeScript

```bash
npm install groq-sdk
```

```typescript
import Groq from "groq-sdk";
const client = new Groq({ apiKey: process.env.GROQ_API_KEY });
```

---

## cURL Examples

### Chat Completion

```bash
curl -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7,
    "max_tokens": 256
  }'
```

### Streaming

```bash
curl -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Tell me a story"}],
    "stream": true
  }'
```

### List Models

```bash
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```
