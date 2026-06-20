# Together AI API Reference — Chat Completions

> **Fetch status:** HTTP 403 Forbidden from https://docs.together.ai/reference/chat-completions — content below is from model training data (knowledge cutoff August 2025).

## Base URL

```
https://api.together.xyz/v1
```

## Authentication

```
Authorization: Bearer YOUR_TOGETHER_API_KEY
Content-Type: application/json
```

---

## POST /v1/chat/completions

Create a chat completion response.

### Request Body

```json
{
  "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ],
  "max_tokens": 512,
  "temperature": 0.7,
  "top_p": 0.7,
  "top_k": 50,
  "repetition_penalty": 1.0,
  "stop": ["</s>"],
  "stream": false,
  "n": 1,
  "safety_model": null,
  "response_format": {"type": "text"},
  "tools": null,
  "tool_choice": "auto",
  "seed": null,
  "logprobs": null,
  "echo": false
}
```

### Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | string | Yes | — | Model ID (e.g., `meta-llama/Llama-3.3-70B-Instruct-Turbo`) |
| `messages` | array | Yes | — | Array of message objects |
| `max_tokens` | integer | No | 512 | Maximum tokens to generate |
| `temperature` | float | No | 0.7 | Randomness (0.0–2.0) |
| `top_p` | float | No | 0.7 | Nucleus sampling (0.0–1.0) |
| `top_k` | integer | No | 50 | Top-k tokens to consider |
| `repetition_penalty` | float | No | 1.0 | Penalize repetition (1.0 = no penalty) |
| `stop` | string/array | No | null | Stop sequences |
| `stream` | boolean | No | false | Stream partial tokens via SSE |
| `n` | integer | No | 1 | Number of completions |
| `safety_model` | string | No | null | Safety/moderation model |
| `response_format` | object | No | `{"type":"text"}` | `"text"` or `"json_object"` |
| `tools` | array | No | null | Tool/function definitions |
| `tool_choice` | string/object | No | `"auto"` | Tool selection mode |
| `seed` | integer | No | null | Random seed for determinism |
| `logprobs` | integer | No | null | Number of token logprobs to return |
| `echo` | boolean | No | false | Include prompt tokens in response |

### Message Object

```json
{
  "role": "user",
  "content": "Hello"
}
```

For tool results:
```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "content": "{\"result\": 42}"
}
```

For vision (multimodal):
```json
{
  "role": "user",
  "content": [
    {"type": "text", "text": "What is in this image?"},
    {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
  ]
}
```

### Tool Definition

```json
{
  "type": "function",
  "function": {
    "name": "function_name",
    "description": "Description of what this function does",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {
          "type": "string",
          "description": "Description of param1"
        }
      },
      "required": ["param1"]
    }
  }
}
```

---

### Response Object

```json
{
  "id": "8857c763d9864571a4b3b9a8",
  "object": "chat.completion",
  "created": 1719000000,
  "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
  "prompt": [],
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Paris is the capital of France.",
        "tool_calls": null
      },
      "finish_reason": "eos",
      "seed": null,
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 28,
    "completion_tokens": 8,
    "total_tokens": 36
  }
}
```

### Response with Tool Calls

```json
{
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"San Francisco, CA\", \"unit\": \"fahrenheit\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

### Streaming Response (SSE)

```
data: {"id":"chatcmpl-abc","object":"chat.completion.chunk","created":1719000000,"model":"meta-llama/Llama-3.3-70B-Instruct-Turbo","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"chatcmpl-abc","object":"chat.completion.chunk","created":1719000000,"model":"meta-llama/Llama-3.3-70B-Instruct-Turbo","choices":[{"index":0,"delta":{"content":"Paris"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc","object":"chat.completion.chunk","created":1719000000,"model":"meta-llama/Llama-3.3-70B-Instruct-Turbo","choices":[{"index":0,"delta":{"content":" is"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc","object":"chat.completion.chunk","created":1719000000,"model":"meta-llama/Llama-3.3-70B-Instruct-Turbo","choices":[{"index":0,"delta":{},"finish_reason":"eos"}],"usage":{"prompt_tokens":28,"completion_tokens":5,"total_tokens":33}}

data: [DONE]
```

---

## POST /v1/completions

Legacy completions endpoint (not chat format).

```json
{
  "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
  "prompt": "Once upon a time",
  "max_tokens": 100,
  "temperature": 0.7,
  "top_p": 0.7,
  "top_k": 50,
  "repetition_penalty": 1.0,
  "stop": ["</s>"],
  "stream": false
}
```

---

## POST /v1/embeddings

Generate vector embeddings.

```json
{
  "model": "BAAI/bge-large-en-v1.5",
  "input": "The quick brown fox"
}
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.123, -0.456, ...],  // 1024-dimensional vector
      "index": 0
    }
  ],
  "model": "BAAI/bge-large-en-v1.5",
  "usage": {
    "prompt_tokens": 6,
    "total_tokens": 6
  }
}
```

Batch embeddings:
```json
{
  "model": "BAAI/bge-large-en-v1.5",
  "input": ["First text", "Second text", "Third text"]
}
```

---

## POST /v1/images/generations

Generate images.

```json
{
  "model": "black-forest-labs/FLUX.1-schnell",
  "prompt": "A beautiful sunset over mountains",
  "n": 1,
  "width": 1024,
  "height": 1024,
  "steps": 4,
  "seed": null,
  "response_format": "url"
}
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | string | required | Image model ID |
| `prompt` | string | required | Text description |
| `n` | integer | 1 | Number of images |
| `width` | integer | 1024 | Image width (pixels) |
| `height` | integer | 1024 | Image height (pixels) |
| `steps` | integer | 20 | Diffusion steps |
| `seed` | integer | null | Random seed |
| `response_format` | string | "url" | "url" or "b64_json" |
| `negative_prompt` | string | null | What to avoid |

---

## GET /v1/models

List all available models.

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
      "object": "model",
      "type": "chat",
      "context_length": 131072,
      "pricing": {
        "input": 0.00000088,
        "output": 0.00000088
      }
    }
  ]
}
```

---

## Fine-Tuning Endpoints

### POST /v1/fine-tunes

Create a fine-tune job.

```json
{
  "training_file": "file-abc123",
  "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
  "n_epochs": 3,
  "n_checkpoints": 1,
  "batch_size": 16,
  "learning_rate": 1e-5,
  "suffix": "my-model",
  "wandb_api_key": null
}
```

### GET /v1/fine-tunes

List all fine-tune jobs.

### GET /v1/fine-tunes/{id}

Get a specific fine-tune job.

### POST /v1/fine-tunes/{id}/cancel

Cancel a fine-tune job.

---

## Files Endpoints

### POST /v1/files

Upload a file for fine-tuning.

```
Content-Type: multipart/form-data
file: <binary data>
purpose: fine-tune
```

### GET /v1/files

List uploaded files.

### GET /v1/files/{id}

Get file metadata.

### DELETE /v1/files/{id}

Delete a file.

---

## Error Responses

```json
{
  "error": {
    "message": "Invalid API key",
    "type": "invalid_api_key",
    "code": 401
  }
}
```

| HTTP Code | Error Type | Description |
|---|---|---|
| 400 | `invalid_request` | Bad request parameters |
| 401 | `invalid_api_key` | Authentication failed |
| 404 | `not_found` | Model/resource not found |
| 422 | `validation_error` | Parameter validation failed |
| 429 | `rate_limit_exceeded` | Too many requests |
| 500 | `server_error` | Internal server error |
| 503 | `service_unavailable` | Service temporarily down |

---

## cURL Examples

### Chat Completion

```bash
curl -X POST https://api.together.xyz/v1/chat/completions \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 512,
    "temperature": 0.7
  }'
```

### Embeddings

```bash
curl -X POST https://api.together.xyz/v1/embeddings \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "BAAI/bge-large-en-v1.5",
    "input": "Hello world"
  }'
```

### List Models

```bash
curl https://api.together.xyz/v1/models \
  -H "Authorization: Bearer $TOGETHER_API_KEY"
```

---

## SDK Installation

```bash
# Python
pip install together

# JavaScript
npm install together-ai
```
