# HuggingFace Inference API (Serverless)
> Source: https://huggingface.co/docs/api-inference/index
> Fetched: 2026-06-20

## Overview

The HuggingFace Serverless Inference API (also called "HF Inference" within the Inference Providers system) is a hosted service that allows developers to run inference on thousands of pre-trained models hosted on the Hub without managing any infrastructure. Previously known as "Inference API (serverless)", it is now integrated into the broader Inference Providers system.

The API accepts HTTPS requests to any model hosted on the Hub. HuggingFace handles model loading, GPU/CPU allocation, and scaling automatically.

## Authentication

All requests require a HuggingFace User Access Token passed as a Bearer token in the Authorization header:

```
Authorization: Bearer hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Or using environment variable:

```bash
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

To create a token:
1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click "New token"
3. For inference, create a fine-grained token with **"Make calls to Inference Providers"** permission
4. A "read" token also works for public models

> **Important**: Always pass an HF_TOKEN. Missing tokens are the number one reason users get rate limited.

## Endpoint URL Format

```
POST https://api-inference.huggingface.co/models/{model_id}
```

Example:
```bash
curl -X POST \
  https://api-inference.huggingface.co/models/gpt2 \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "The answer to the universe is"}'
```

## Free Tier vs Pro

### Free Tier
- Access to thousands of models for experimentation
- Rate limited: approximately **~1000 requests/day** (strict limit; 429 errors when exceeded)
- Models may "cold start" — first request after idle period takes 3–10 seconds (model loads into memory)
- Models spin down after ~15 minutes of inactivity
- Sufficient for exploration and prototyping

### PRO Account ($9/month)
- Higher rate limits and quota amounts
- $2/month of usage credits included
- After credits are exhausted, billed per request based on compute time × hardware cost per second
- Access to more powerful models and higher throughput

### Enterprise Hub
- Highest quota amounts available on request
- Organization-level billing and access control

## Rate Limits

Rate limits are based on number of requests (may shift to compute-based or token-based in future):
- Without token: Very low (not recommended)
- With free token: ~1000 requests/day
- PRO: Higher limits
- Enterprise: Highest limits available on request

See: [https://huggingface.co/docs/api-inference/en/rate-limits](https://huggingface.co/docs/api-inference/en/rate-limits)

## Supported Tasks

The HF Inference provider (which powers the Serverless API) focuses primarily on:
- **CPU inference**: text embeddings, text ranking, text classification, token classification
- **Smaller LLMs**: models with historical importance (BERT, GPT-2, DistilBERT, etc.)
- **Text generation** (smaller models)
- **Image classification**
- **Speech recognition** (smaller models)
- **Translation**
- **Summarization**

> **Note**: As of July 2025, hf-inference focuses mostly on CPU inference and smaller LLMs. For larger, more capable models (LLaMA, Mistral, Qwen, etc.), use the Inference Providers router with third-party providers.

## How to Call Models

### Raw HTTP (curl)

```bash
# Text generation
curl -X POST \
  https://api-inference.huggingface.co/models/gpt2 \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "The capital of France is"}'

# Text classification
curl -X POST \
  https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "I love using HuggingFace!"}'
```

### Python (requests)

```python
import requests
import os

API_URL = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

output = query({"inputs": "The answer to the universe is"})
```

### Python (huggingface_hub InferenceClient)

```python
from huggingface_hub import InferenceClient

client = InferenceClient(token=os.environ["HF_TOKEN"])

# Text generation
result = client.text_generation("The capital of France is", model="gpt2")

# Chat completion (OpenAI-compatible)
result = client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Model Cold Start

- First request after a model has been idle returns `{"estimated_time": N}` with HTTP 503
- Retry after waiting for `estimated_time` seconds
- Subsequent requests are fast (~500ms)
- Models spin down after ~15 minutes of inactivity

## Migration Note

The legacy `api-inference.huggingface.co` endpoint is still available but HuggingFace recommends migrating to the new Inference Providers system (`router.huggingface.co/v1`) for access to more capable models and providers. See [inference-router.md](./inference-router.md).

## References

- [Serverless Inference API Docs](https://huggingface.co/docs/api-inference/index)
- [Inference Providers Overview](https://huggingface.co/docs/inference-providers/index)
- [Rate Limits](https://huggingface.co/docs/api-inference/en/rate-limits)
- [Pricing](https://huggingface.co/docs/inference-providers/pricing)
- [PRO Account](https://huggingface.co/pro)
