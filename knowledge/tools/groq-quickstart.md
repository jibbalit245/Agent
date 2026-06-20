# Groq Quickstart

> **Fetch status:** HTTP 403 Forbidden from https://console.groq.com/docs/quickstart — content below is from model training data (knowledge cutoff August 2025).

## Overview

Groq provides ultra-fast LLM inference via a simple REST API and official Python/JS SDKs. This guide covers setup and your first API call.

---

## Step 1: Get an API Key

1. Visit https://console.groq.com/
2. Sign up or log in
3. Go to **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_...`)

---

## Step 2: Install the SDK

### Python

```bash
pip install groq
```

### Node.js / TypeScript

```bash
npm install groq-sdk
# or
yarn add groq-sdk
```

---

## Step 3: Set Your API Key

### Environment Variable (recommended)

```bash
export GROQ_API_KEY="gsk_your_key_here"
```

### In code (not recommended for production)

```python
client = Groq(api_key="gsk_your_key_here")
```

---

## Step 4: First API Call

### Python

```python
from groq import Groq

client = Groq()  # reads GROQ_API_KEY from environment

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)
```

### JavaScript

```javascript
import Groq from "groq-sdk";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

async function main() {
  const completion = await groq.chat.completions.create({
    messages: [
      {
        role: "user",
        content: "Explain the importance of fast language models",
      },
    ],
    model: "llama-3.3-70b-versatile",
  });

  console.log(completion.choices[0]?.message?.content || "");
}

main();
```

### cURL

```bash
curl -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [
      {
        "role": "user",
        "content": "Explain the importance of fast language models"
      }
    ]
  }'
```

---

## Step 5: Streaming

### Python Streaming

```python
from groq import Groq

client = Groq()

stream = client.chat.completions.create(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="llama-3.3-70b-versatile",
    stream=True,
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
print()
```

### JavaScript Streaming

```javascript
const stream = await groq.chat.completions.create({
  messages: [{ role: "user", content: "Tell me a story" }],
  model: "llama-3.3-70b-versatile",
  stream: true,
});

for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content || "");
}
```

---

## Response Structure

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
        "content": "Fast language models are important because..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 150,
    "total_tokens": 170
  },
  "system_fingerprint": "fp_abc123",
  "x_groq": {
    "id": "req_abc123"
  }
}
```

---

## Key Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | string | required | Model ID to use |
| `messages` | array | required | Conversation history |
| `temperature` | float | 1.0 | Randomness (0.0–2.0) |
| `max_tokens` | integer | model max | Max tokens to generate |
| `top_p` | float | 1.0 | Nucleus sampling |
| `stream` | boolean | false | Enable streaming |
| `stop` | string/array | null | Stop sequences |
| `n` | integer | 1 | Number of completions |

---

## Next Steps

- See [groq-models.md] for all available models
- See [groq-text-chat.md] for advanced chat features
- See [groq-tool-use.md] for function calling
- See [groq-rate-limits.md] for limits and retry logic
