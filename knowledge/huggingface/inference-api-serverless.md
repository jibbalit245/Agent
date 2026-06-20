# HuggingFace Serverless Inference API
> Sources: https://huggingface.co/learn/cookbook/en/enterprise_hub_serverless_inference_api, https://klymentiev.com/blog/huggingface-inference-api, https://techjacksolutions.com/ai-tools/hugging-face/hugging-face-inference-api/, https://discuss.huggingface.co/t/whats-the-rate-limit/83172, https://discuss.huggingface.co/t/serverless-inference-api-credits/155900/2, https://huggingface.co/docs/inference-providers/pricing, WebSearch results 2026-06-20
> Fetched: 2026-06-20

---

## Overview

The HuggingFace Serverless Inference API lets you run ML inference on thousands of models hosted on the HuggingFace Hub without managing any infrastructure. You send an HTTP request, HuggingFace loads the model and returns results.

**Important architectural note (2025):** The legacy Serverless Inference API (`api-inference.huggingface.co`) is now considered the `hf-inference` provider within the new Inference Providers system. For large LLMs, the recommended path is the **Inference Router** (`router.huggingface.co/v1`) with third-party providers. The serverless API (`hf-inference`) focuses on CPU inference, embeddings, and smaller models.

---

## Endpoints

### Legacy Serverless (still active)
```
POST https://api-inference.huggingface.co/models/{model_id}
```

### Via Inference Providers (recommended)
```
POST https://router.huggingface.co/v1/chat/completions
```
With model format: `model-id:hf-inference` (or other provider)

---

## Authentication

```bash
# Environment variable (recommended)
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# HTTP header
Authorization: Bearer hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Critical:** Always pass a token. Users without tokens get extremely low (essentially zero) rate limits and are the most common reason for 429 errors.

---

## Free Tier vs PRO Limits

| Feature | Free Tier | PRO ($9/mo) | Enterprise |
|---------|-----------|-------------|------------|
| Monthly included credits | ~$0.10 | $2.00 | $2.00/seat |
| Rate limits | Low (~few hundred/hr on popular models) | Higher (~8x more quota) | Highest |
| ZeroGPU quota | 5 min/day | 40 min/day | 40-60 min/day |
| Pay-as-you-go | No | Yes (after credits) | Yes (after credits) |
| Model access | Public models | Public + more | All |

**Note:** Exact rate limits are not published as fixed numbers. HuggingFace describes them as "rate-limited" with limits varying by model popularity and server load. The 5-minute fixed window system means burst patterns may hit limits even at low average rates.

---

## Supported Tasks (hf-inference provider)

The hf-inference (serverless) provider supports these task types:

**Text/NLP:**
- `text-generation` — autoregressive text completion
- `text2text-generation` — encoder-decoder generation (T5, BART)
- `text-classification` / `sentiment-analysis`
- `token-classification` — NER, POS tagging
- `fill-mask` — masked language model predictions
- `summarization`
- `translation` — e.g., `Helsinki-NLP/opus-mt-en-fr`
- `question-answering`
- `conversational` (deprecated; use chat-completion)
- `zero-shot-classification`
- `table-question-answering`

**Multimodal / Vision:**
- `image-classification`
- `image-segmentation`
- `object-detection`
- `zero-shot-image-classification`
- `image-to-text` — image captioning

**Audio:**
- `automatic-speech-recognition`
- `audio-classification`

**Embeddings:**
- `feature-extraction` — returns raw embeddings/vectors
- `sentence-similarity`

**Image Generation:**
- `text-to-image` — via hf-inference or dedicated providers

**Chat (via Inference Providers router):**
- `chat-completion` — OpenAI-compatible, routes to providers

---

## Python Client Examples

### Using InferenceClient (recommended)

```python
from huggingface_hub import InferenceClient
import os

client = InferenceClient(token=os.environ["HF_TOKEN"])

# Text generation (smaller/base models)
result = client.text_generation(
    prompt="The capital of France is",
    model="gpt2",
    max_new_tokens=50,
)
print(result)  # Returns plain string

# Text classification
result = client.text_classification(
    text="I love this product!",
    model="distilbert-base-uncased-finetuned-sst-2-english",
)
# Returns: [{"label": "POSITIVE", "score": 0.9998}]

# Feature extraction / embeddings
embeddings = client.feature_extraction(
    text="What is machine learning?",
    model="sentence-transformers/all-MiniLM-L6-v2",
)
# Returns numpy array

# Summarization
summary = client.summarization(
    text="Very long article text here...",
    model="facebook/bart-large-cnn",
)

# Translation
translation = client.translation(
    text="Hello, how are you?",
    model="Helsinki-NLP/opus-mt-en-fr",
)

# ASR
transcript = client.automatic_speech_recognition(
    audio=open("audio.wav", "rb").read(),
    model="openai/whisper-large-v3",
)
print(transcript.text)
```

### Using raw requests

```python
import requests
import os

headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}

def query(model_id: str, payload: dict) -> dict:
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# Text generation
output = query("gpt2", {"inputs": "The future of AI is"})

# With wait_for_model (avoids 503 on cold start)
output = query("gpt2", {
    "inputs": "Hello world",
    "options": {"wait_for_model": True}
})
```

### Chat completion for LLMs (via Inference Router)

```python
from huggingface_hub import InferenceClient

# For large LLMs, use a provider like featherless-ai or together
client = InferenceClient(
    provider="featherless-ai",
    api_key=os.environ["HF_TOKEN"],
)

response = client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain neural networks briefly."},
    ],
    max_tokens=200,
    temperature=0.7,
)
print(response.choices[0].message.content)
```

---

## Model Cold Start

When a model has been idle, the first request triggers a "cold start":

**Response during cold start:**
```json
{"error": "Model is currently loading", "estimated_time": 20.0}
```
HTTP status: **503 Service Unavailable**

**Handling cold starts:**

```python
import time
import requests

def query_with_retry(model_id: str, payload: dict, max_retries: int = 5) -> dict:
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}
    
    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 503:
            data = response.json()
            wait_time = data.get("estimated_time", 20.0)
            print(f"Model loading, waiting {wait_time}s...")
            time.sleep(wait_time)
            continue
        
        if response.status_code == 200:
            return response.json()
        
        response.raise_for_status()
    
    raise RuntimeError("Max retries exceeded")

# Or use the options flag to have HF wait for you:
output = query("gpt2", {
    "inputs": "test",
    "options": {"wait_for_model": True}  # HF waits up to 60s
})
```

---

## Billing and Credits

- Free users: ~$0.10/month in inference credits (subject to change)
- PRO users: $2.00/month in inference credits
- After credits are exhausted: pay-as-you-go at provider rates
- Billing tracked at: https://huggingface.co/settings/billing
- No per-request fees for models within the `hf-inference` provider on the free tier — purely rate-limited

---

## Differences: hf-inference vs Third-Party Providers

| Feature | hf-inference (serverless) | Third-party (featherless, together, etc.) |
|---------|--------------------------|-------------------------------------------|
| Model size | Small to medium | Large (7B–400B+) |
| Compute | CPU + small GPU | GPU (A100, H100, etc.) |
| Cold starts | Yes | Minimal (pre-loaded) |
| Rate limits | Low | Higher (depends on plan/credits) |
| Best for | Embeddings, classification, small NLP | Large LLM chat, image generation |
| Cost | Very cheap / free tier | Per-token or per-second billing |

---

## References

- [Serverless Inference API Cookbook](https://huggingface.co/learn/cookbook/en/enterprise_hub_serverless_inference_api)
- [Inference Providers Index](https://huggingface.co/docs/inference-providers/en/index)
- [InferenceClient API Reference](https://huggingface.co/docs/huggingface_hub/package_reference/inference_client)
- [Pricing and Billing](https://huggingface.co/docs/inference-providers/pricing)
- [PRO Account](https://huggingface.co/pro)
