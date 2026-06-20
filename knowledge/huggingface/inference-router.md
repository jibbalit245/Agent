# HuggingFace Inference Router (router.huggingface.co/v1)
> Source: https://huggingface.co/docs/inference-providers/index
> Fetched: 2026-06-20

## Overview

The HuggingFace Inference Router is an **OpenAI-compatible** inference endpoint that provides unified access to hundreds of ML models across multiple inference providers. It is the successor to the legacy Serverless Inference API and is the recommended way to access powerful LLMs and other models through HuggingFace.

**Base URL**: `https://router.huggingface.co/v1`

This endpoint is fully compatible with the OpenAI API, meaning any client that works with OpenAI (Python SDK, JS SDK, raw HTTP) can be pointed at `router.huggingface.co/v1` with a HuggingFace token and it will work.

## How It Differs from the Standard Inference API

| Feature | Legacy Inference API | Inference Router |
|---------|---------------------|-----------------|
| Base URL | `api-inference.huggingface.co/models/` | `router.huggingface.co/v1` |
| Protocol | Task-specific endpoints | OpenAI-compatible (`/chat/completions`, `/completions`) |
| Provider | HF only (CPU/small models) | 20+ providers (GPU, large models) |
| Model selection | Model ID only | `model-id:provider` format |
| Capability | Smaller models, CPU | Large LLMs, GPU inference |
| Billing | Free with rate limits | Per-provider billing via HF account |

## Authentication

Use your HuggingFace User Access Token as a Bearer token:

```bash
Authorization: Bearer hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

For the Inference Router specifically, the token should have the **"Make calls to Inference Providers"** permission (available with fine-grained tokens).

With a single HuggingFace token, requests are proxied through HuggingFace's infrastructure and billed to your HuggingFace account at standard provider rates.

You can also use your own provider API key directly (e.g., your own Featherless AI key), but using the HF token is the simpler path.

## Model Format: `model-id:provider`

This is the critical format for using the Inference Router. When calling the OpenAI-compatible endpoint, specify the model as:

```
{model-id}:{provider}
```

Examples:
- `meta-llama/Llama-3.1-8B-Instruct:featherless-ai`
- `deepseek-ai/DeepSeek-V3:together`
- `mistralai/Mistral-7B-Instruct-v0.2:nebius`
- `openai/gpt-oss-120b:sambanova`

### Provider Selection Policies

Instead of a specific provider, you can use a policy keyword:
- `:fastest` (default) — routes to the fastest available provider for that model
- `:cheapest` — routes to the most cost-efficient available provider
- `:preferred` — follows your preference order set in your HF account settings

## Available Providers

As of 2025-2026, supported providers include:
- `black-forest-labs`
- `cerebras`
- `clarifai`
- `cohere`
- `deepinfra`
- `fal-ai`
- `featherless-ai` (largest catalog: 6,700+ models)
- `fireworks-ai`
- `groq`
- `hf-inference` (HF's own CPU inference)
- `hyperbolic`
- `nebius`
- `novita`
- `nscale`
- `nvidia`
- `openai`
- `ovhcloud`
- `publicai`
- `replicate`
- `sambanova`
- `scaleway`
- `together`
- `wavespeed`
- `zai-org`

## Using with OpenAI Python SDK

Drop-in replacement for OpenAI:

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct:featherless-ai",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    max_tokens=256,
)

print(response.choices[0].message.content)
```

## Using with huggingface_hub InferenceClient

The `InferenceClient` natively supports the router — no need to set `base_url`:

```python
from huggingface_hub import InferenceClient
import os

client = InferenceClient(
    provider="featherless-ai",
    api_key=os.environ["HF_TOKEN"],
)

response = client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## Using with Raw HTTP

```bash
curl https://router.huggingface.co/v1/chat/completions \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.1-8B-Instruct:featherless-ai",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Billing Through the Router

When using the router with your HF token:
- Calls are proxied through HuggingFace
- Usage is billed to your HuggingFace account at the underlying provider's rates
- You get a unified bill via HuggingFace instead of managing multiple provider accounts
- Every user gets monthly free-tier credits to experiment
- After credits are exhausted, charges apply per request (compute time × hardware cost)

You can alternatively set your own API keys for specific providers in your HF account settings, in which case those calls use your personal provider account.

## Automatic Failover

When using the `:fastest` policy (default), the router automatically fails over to the next available provider if the first one is unavailable, ensuring higher reliability.

## Migration from Legacy API

The legacy `api-inference.huggingface.co` endpoint is deprecated. Migrate by:
1. Changing `base_url` from `https://api-inference.huggingface.co/models/` to `https://router.huggingface.co/v1`
2. Using OpenAI-compatible message format (`chat/completions` endpoint)
3. Appending `:provider` to model names (or use `:fastest` for automatic selection)

## References

- [Inference Providers Docs](https://huggingface.co/docs/inference-providers/index)
- [HF Inference Provider (hf-inference)](https://huggingface.co/docs/inference-providers/en/providers/hf-inference)
- [Featherless AI Provider](https://huggingface.co/docs/inference-providers/en/providers/featherless-ai)
- [Inference Providers OpenAI-Compatible Announcement](https://huggingface.co/changelog/inference-providers-openai-compatible)
- [Pricing and Billing](https://huggingface.co/docs/inference-providers/pricing)
