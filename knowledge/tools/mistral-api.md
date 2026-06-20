# Mistral AI API Reference

> **Fetch status:** HTTP 403 Forbidden from https://docs.mistral.ai/api/ — content below is from model training data (knowledge cutoff August 2025).

## Base URL

```
https://api.mistral.ai/v1
```

For Codestral (separate key):
```
https://codestral.mistral.ai/v1
```

## Authentication

```
Authorization: Bearer YOUR_MISTRAL_API_KEY
Content-Type: application/json
```

---

## Endpoints

### POST /v1/chat/completions

Create a chat completion.

**Request Body:**

```json
{
  "model": "mistral-large-latest",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "top_p": 1.0,
  "max_tokens": null,
  "stream": false,
  "safe_prompt": false,
  "random_seed": null,
  "response_format": {"type": "text"},
  "tools": null,
  "tool_choice": "auto"
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | string | Yes | — | Model ID |
| `messages` | array | Yes | — | Conversation history |
| `temperature` | float | No | 0.7 | Randomness (0.0–1.0) |
| `top_p` | float | No | 1.0 | Nucleus sampling |
| `max_tokens` | integer | No | null | Max tokens to generate |
| `stream` | boolean | No | false | Enable streaming |
| `safe_prompt` | boolean | No | false | Prepend safety system prompt |
| `random_seed` | integer | No | null | Seed for reproducibility |
| `response_format` | object | No | `{"type":"text"}` | `"text"` or `"json_object"` |
| `tools` | array | No | null | Tool definitions |
| `tool_choice` | string/object | No | `"auto"` | Tool selection |

**Note:** Mistral uses `temperature` range 0.0–1.0 (not 0.0–2.0 like OpenAI).

**Response:**

```json
{
  "id": "cmpl-e5cc70bb28c444948073e77776eb30ef",
  "object": "chat.completion",
  "created": 1702256327,
  "model": "mistral-large-latest",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?",
        "tool_calls": null
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 14,
    "completion_tokens": 9,
    "total_tokens": 23
  }
}
```

---

### POST /v1/embeddings

Generate text embeddings.

**Request:**

```json
{
  "model": "mistral-embed",
  "input": ["Hello world", "How are you?"],
  "encoding_format": "float"
}
```

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | string | Yes | — | Embedding model ID |
| `input` | string/array | Yes | — | Text(s) to embed |
| `encoding_format` | string | No | `"float"` | `"float"` or `"base64"` |

**Response:**

```json
{
  "id": "embd-aad6fc62b17349b192ef09225058bc45",
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.0165, -0.0123, ...],
      "index": 0
    },
    {
      "object": "embedding",
      "embedding": [-0.0234, 0.0456, ...],
      "index": 1
    }
  ],
  "model": "mistral-embed",
  "usage": {
    "prompt_tokens": 5,
    "total_tokens": 5
  }
}
```

---

### POST /v1/fim/completions

Fill-in-middle completions (Codestral).

```json
{
  "model": "codestral-latest",
  "prompt": "def calculate_sum(a, b):\n    ",
  "suffix": "\n    return result",
  "max_tokens": 100,
  "temperature": 0.0
}
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `model` | string | Yes | Must be Codestral |
| `prompt` | string | Yes | Code before insertion point |
| `suffix` | string | No | Code after insertion point |
| `max_tokens` | integer | No | Max tokens |
| `temperature` | float | No | Randomness |
| `stop` | string/array | No | Stop sequences |

**Response:**

```json
{
  "id": "cmpl-abc123",
  "object": "completion",
  "created": 1719000000,
  "model": "codestral-latest",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "result = a + b"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 8,
    "total_tokens": 23
  }
}
```

---

### GET /v1/models

List available models.

```bash
curl https://api.mistral.ai/v1/models \
  -H "Authorization: Bearer $MISTRAL_API_KEY"
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "mistral-large-latest",
      "object": "model",
      "created": 1719000000,
      "owned_by": "mistralai",
      "capabilities": {
        "completion_chat": true,
        "completion_fim": false,
        "function_calling": true,
        "fine_tuning": true,
        "vision": false
      },
      "max_context_length": 128000,
      "aliases": ["mistral-large-2411"],
      "deprecation": null,
      "default_model_temperature": 0.7,
      "type": "base"
    }
  ]
}
```

---

### GET /v1/models/{model_id}

Retrieve a model.

### DELETE /v1/models/{model_id}

Delete a fine-tuned model.

---

### POST /v1/moderations

Content moderation classification.

```json
{
  "model": "mistral-moderation-latest",
  "input": "Content to classify"
}
```

Or for chat format:
```json
{
  "model": "mistral-moderation-latest",
  "input": [
    {"role": "user", "content": "Is this content safe?"}
  ]
}
```

**Response:**

```json
{
  "id": "mod-abc123",
  "model": "mistral-moderation-latest",
  "results": [
    {
      "categories": {
        "sexual": false,
        "hate_and_discrimination": false,
        "violence_and_threats": false,
        "dangerous_and_criminal_content": false,
        "selfharm": false,
        "health": false,
        "financial": false,
        "law": false,
        "pii": false
      },
      "category_scores": {
        "sexual": 0.001,
        "hate_and_discrimination": 0.002,
        ...
      }
    }
  ]
}
```

---

## Fine-Tuning Endpoints

### POST /v1/fine_tuning/jobs

Create a fine-tune job.

```json
{
  "model": "mistral-small-latest",
  "training_files": [{"file_id": "file-abc123", "weight": 1}],
  "validation_files": null,
  "hyperparameters": {
    "training_steps": 1000,
    "learning_rate": 0.0001
  },
  "suffix": "my-fine-tuned-model",
  "integrations": []
}
```

### GET /v1/fine_tuning/jobs

List fine-tune jobs.

### GET /v1/fine_tuning/jobs/{job_id}

Get a fine-tune job.

### POST /v1/fine_tuning/jobs/{job_id}/cancel

Cancel a fine-tune job.

---

## Files Endpoints

### POST /v1/files

Upload a file.

```bash
curl -X POST https://api.mistral.ai/v1/files \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -F "file=@training_data.jsonl" \
  -F "purpose=fine-tune"
```

### GET /v1/files

List files.

### GET /v1/files/{file_id}

Get file metadata.

### DELETE /v1/files/{file_id}

Delete a file.

---

## Error Codes

| HTTP Status | Description |
|---|---|
| 400 | Bad Request — invalid parameters |
| 401 | Unauthorized — invalid API key |
| 403 | Forbidden — insufficient permissions |
| 404 | Not Found — model/resource not found |
| 422 | Unprocessable Entity — validation error |
| 429 | Too Many Requests — rate limited |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

**Error format:**

```json
{
  "message": "Unauthorized",
  "request_id": "req_abc123"
}
```

---

## SDK Clients

### Python

```bash
pip install mistralai
```

```python
from mistralai import Mistral

client = Mistral(api_key="your_key")

# Async
import asyncio
from mistralai import AsyncMistral

async_client = AsyncMistral(api_key="your_key")
```

### JavaScript

```bash
npm install @mistralai/mistralai
```

```typescript
import { Mistral } from "@mistralai/mistralai";
const client = new Mistral({ apiKey: process.env.MISTRAL_API_KEY });
```

---

## Rate Limits

| Plan | Requests/minute | Tokens/minute |
|---|---|---|
| Free | 1 | 500,000 |
| Developer | 60–600 | 1,000,000+ |
| Enterprise | Custom | Custom |

Rate limit headers returned on every response:
```
x-ratelimit-limit: 1000000
x-ratelimit-remaining: 999972
x-ratelimit-reset: 60
```
