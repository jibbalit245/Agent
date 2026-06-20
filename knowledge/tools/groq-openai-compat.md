# Groq OpenAI Compatibility

> **Fetch status:** HTTP 403 Forbidden from https://console.groq.com/docs/openai — content below is from model training data (knowledge cutoff August 2025).

## Overview

Groq provides an OpenAI-compatible API, meaning you can use the OpenAI Python/JS SDK or any OpenAI-compatible tool by simply changing the `base_url` and `api_key`. No other code changes are required for basic chat completions.

## Base URL

```
https://api.groq.com/openai/v1
```

## Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="your_groq_api_key",
)

completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
)
print(completion.choices[0].message.content)
```

## JavaScript / TypeScript (OpenAI SDK)

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://api.groq.com/openai/v1",
  apiKey: process.env.GROQ_API_KEY,
});

const completion = await client.chat.completions.create({
  model: "llama-3.3-70b-versatile",
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(completion.choices[0].message.content);
```

## Groq Native SDK

```python
from groq import Groq

client = Groq(api_key="your_groq_api_key")

completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(completion.choices[0].message.content)
```

## Supported OpenAI Endpoints

| Endpoint | Supported |
|---|---|
| `POST /chat/completions` | Yes |
| `POST /completions` | Yes (legacy) |
| `GET /models` | Yes |
| `POST /audio/transcriptions` | Yes (Whisper) |
| `POST /audio/translations` | Yes (Whisper) |
| `POST /embeddings` | Limited (via certain models) |

## Unsupported OpenAI Features

- Fine-tuning endpoints
- Image generation (DALL-E)
- Assistants API (threads, runs)
- Files API
- Batch API

## Environment Variable Setup

```bash
export GROQ_API_KEY="gsk_..."
```

## Using with LangChain

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key="your_groq_api_key",
)
```

## Using with LiteLLM

```python
import litellm

response = litellm.completion(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## Key Differences from OpenAI

1. **Speed:** Groq uses custom LPU hardware for significantly faster inference (often 10-100x faster token generation).
2. **Models:** Uses open-source models (Llama, Mixtral, Gemma, etc.) instead of OpenAI proprietary models.
3. **Rate limits:** Different from OpenAI — see groq-rate-limits.md.
4. **No persistent state:** No assistants/threads/files storage.
5. **Context windows:** Vary by model; check groq-models.md.
