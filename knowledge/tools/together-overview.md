# Together AI Overview

> **Fetch status:** HTTP 403 Forbidden from https://docs.together.ai/docs/introduction — content below is from model training data (knowledge cutoff August 2025).

## What is Together AI?

Together AI is a cloud AI platform providing:
- **Inference:** Fast, scalable inference for 100+ open-source models
- **Fine-tuning:** Train custom models on your data
- **Embeddings:** Generate text embeddings
- **Image generation:** Run Stable Diffusion and other image models
- **Dedicated endpoints:** Reserved capacity for production workloads

Together AI is particularly known for competitive pricing, OpenAI-compatible APIs, and hosting many state-of-the-art open models.

---

## Base URL

```
https://api.together.xyz/v1
```

Also accessible as:
```
https://api.together.ai/v1
```

---

## Authentication

```bash
export TOGETHER_API_KEY="your_api_key_here"
```

All requests use Bearer token authentication:
```
Authorization: Bearer your_api_key_here
```

---

## Key Features

| Feature | Description |
|---|---|
| **Serverless inference** | Pay-per-token, no setup needed |
| **Dedicated instances** | Reserved GPU capacity |
| **Fine-tuning** | Full fine-tuning and LoRA support |
| **OpenAI compatibility** | Drop-in replacement for OpenAI SDK |
| **100+ models** | Llama, Mistral, Qwen, FLUX, and more |
| **Function calling** | Tool use on supported models |
| **JSON mode** | Structured output |
| **Vision** | Multimodal models available |

---

## Quick Start

### Install SDK

```bash
pip install together
```

### Python Example

```python
from together import Together

client = Together(api_key="your_api_key")

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "Hello!"}],
)

print(response.choices[0].message.content)
```

### OpenAI SDK Compatibility

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key="your_together_api_key",
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### JavaScript

```javascript
import Together from "together-ai";

const client = new Together({ apiKey: process.env.TOGETHER_API_KEY });

const response = await client.chat.completions.create({
  model: "meta-llama/Llama-3.3-70B-Instruct-Turbo",
  messages: [{ role: "user", content: "Hello!" }],
});

console.log(response.choices[0].message.content);
```

---

## API Categories

### 1. Chat Completions
Conversational AI with multi-turn support.
- Endpoint: `POST /v1/chat/completions`

### 2. Completions (Legacy)
Single-prompt text generation.
- Endpoint: `POST /v1/completions`

### 3. Embeddings
Generate vector representations of text.
- Endpoint: `POST /v1/embeddings`

### 4. Images
Generate images from text prompts.
- Endpoint: `POST /v1/images/generations`

### 5. Fine-tuning
Train custom models.
- Endpoints: `/v1/fine-tunes/*`

### 6. Files
Upload training data.
- Endpoints: `/v1/files/*`

---

## Supported Frameworks

- **LangChain:** `langchain-together` or via OpenAI compat
- **LlamaIndex:** Via OpenAI compat
- **LiteLLM:** `together_ai/model-name`
- **Vercel AI SDK:** Via OpenAI compat
- **Haystack:** Via OpenAI compat

---

## Console

Dashboard at: https://api.together.ai/
- View usage and costs
- Manage API keys
- Browse available models
- Start fine-tuning jobs
- Deploy dedicated endpoints
